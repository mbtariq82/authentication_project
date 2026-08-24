import os

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
                "AGENT_DATABASE_URL environment variable is not configured"
            )

        return SQLDatabase.from_uri(database_url)

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
            if keyword in query_upper:
                return {
                    "error": f"Blocked SQL operation: {keyword}"
                }

        return {
            "error": ""
        }

    def _execute_sql(self, state: AgentState):
        if state.get("error"):
            return {
                "query_result": state["error"]
            }

        try:
            result = self.db.run(
                state["sql_query"]
            )

            return {
                "query_result": (
                    str(result)
                    if result
                    else "No results found."
                )
            }

        except Exception as e:
            return {
                "query_result":
                    f"Error executing query: {str(e)}"
            }

    def _generate_answer(self, state: AgentState):
        if state.get("error"):
            return {
                "final_answer": state["error"]
            }

        prompt = ChatPromptTemplate.from_template(
            """
You are an assistant for a banking admin dashboard.

Answer the administrator's question using
the SQL result.

Question:
{question}

SQL query:
{sql_query}

Database result:
{query_result}

Give a short and clear answer.

Do not mention implementation details unless necessary.
"""
        )

        chain = prompt | self.llm

        response = chain.invoke(
            {
                "question": state["question"],
                "sql_query": state["sql_query"],
                "query_result": state["query_result"],
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

            "raw_result": result.get(
                "query_result",
                "",
            ),

            "answer": result.get(
                "final_answer",
                "",
            ),
        }