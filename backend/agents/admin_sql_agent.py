import os
import re
from sqlalchemy import create_engine, text

from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

from agents.agent_state import AgentState


class AdminSQLAgent:

    def __init__(self):
        self.db = self._connect_db()

        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            temperature=0,
        )

        self.app = self._build_graph()

    def _connect_db(self):
        database_url = os.getenv("AGENT_DATABASE_URL")

        if not database_url:
            raise RuntimeError(
                "AGENT_DATABASE_URL is not configured"
            )

        self.engine = create_engine(database_url)

        return SQLDatabase(self.engine)

    def _get_schema(self, state: AgentState):
        schema = self.db.get_table_info(
            table_names=[
                "users",
                "accounts",
                "loans",
                "cards",
            ]
        )

        return {
            "schema": schema
        }

    def _generate_sql(self, state: AgentState):
        prompt = ChatPromptTemplate.from_template(
            """
            You are a PostgreSQL expert working with a banking database.

            Generate a PostgreSQL SELECT query that answers
            the administrator's question.

            Database schema:

            {schema}

            Admin question:

            {question}

            Rules:

            - Return ONLY SQL.
            - Generate PostgreSQL syntax.
            - Only SELECT statements are allowed.
            - Never use INSERT.
            - Never use UPDATE.
            - Never use DELETE.
            - Never use DROP.
            - Never use ALTER.
            - Never use TRUNCATE.
            - Never modify database data.
            - Exclude soft-deleted records when appropriate.
            - Use JOINs when necessary.
            - Prefer explicit column names instead of SELECT *.
            - Use LIMIT 20 unless the user explicitly requests another amount.

            SQL:
            """
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "schema": state["schema"],
                "question": state["question"],
            }
        )

        sql = (
            response.content
            .strip()
            .replace("```sql", "")
            .replace("```", "")
            .strip()
        )

        return {
            "sql_query": sql
        }

    def _validate_sql(self, state: AgentState):
        query = state["sql_query"].strip()
        query_upper = query.upper()

        blocked_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "CREATE",
            "GRANT",
            "REVOKE",
        ]

        if not query_upper.startswith("SELECT"):
            return {
                "error": "Only SELECT queries are allowed."
            }

        for keyword in blocked_keywords:
            # Whole-word match only — a plain substring check would
            # false-positive on column/alias names that happen to
            # contain a blocked word, e.g. "is_deleted" contains
            # "DELETE", or "recreated_view" would contain "CREATE".
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, query_upper):
                return {
                    "error": f"Blocked SQL operation: {keyword}"
                }

        return {
            "error": ""
        }

    def _execute_sql(self, state: AgentState):

        if state.get("error"):
            return {
                "query_result": []
            }

        try:
            with self.engine.connect() as connection:

                result = connection.execute(
                    text(state["sql_query"])
                )

                rows = [
                    dict(row._mapping)
                    for row in result
                ]

                return {
                    "query_result": rows
                }

        except Exception as e:
            return {
                "error": f"Error executing query: {str(e)}",
                "query_result": [],
            }

    def _generate_answer(self, state: AgentState):

        if state.get("error"):
            return {
                "final_answer": state["error"]
            }

        prompt = ChatPromptTemplate.from_template(
            """
            You are an assistant for a banking admin dashboard.

            Question:
            {question}

            PostgreSQL Query:
            {sql_query}

            Database Result:
            {query_result}

            Provide a short and clear natural language answer.
            """
                )

        chain = prompt | self.llm

        response = chain.invoke(
                    {
                        "question": state["question"],
                        "sql_query": state["sql_query"],
                        "query_result": str(state["query_result"]),
                    }
                )

        return {
                    "final_answer": response.content
                }

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node(
            "get_schema",
            self._get_schema,
        )

        workflow.add_node(
            "generate_sql",
            self._generate_sql,
        )

        workflow.add_node(
            "validate_sql",
            self._validate_sql,
        )

        workflow.add_node(
            "execute_sql",
            self._execute_sql,
        )

        workflow.add_node(
            "generate_answer",
            self._generate_answer,
        )

        workflow.add_edge(
            START,
            "get_schema",
        )

        workflow.add_edge(
            "get_schema",
            "generate_sql",
        )

        workflow.add_edge(
            "generate_sql",
            "validate_sql",
        )

        workflow.add_edge(
            "validate_sql",
            "execute_sql",
        )

        workflow.add_edge(
            "execute_sql",
            "generate_answer",
        )

        workflow.add_edge(
            "generate_answer",
            END,
        )

        return workflow.compile()

    def query(
        self,
        question: str,
    ) -> dict:

        result = self.app.invoke(
            {
                "question": question
            }
        )

        return {
            "question": question,

            "sql_query": result.get(
                "sql_query",
                "",
            ),

            "rows": result.get(
                "query_result",
                [],
            ),

            "answer": result.get(
                "final_answer",
                "",
            ),
        }