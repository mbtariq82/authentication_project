TO DO:
- zod
- interactive UI component

components
    ¦
    V
hooks
    ¦
    V
api

React concepts:
- components: 
    - function that returns JSX (HTML-like syntax written for React components)
    - conceptually: reusable UI parts
- props: read-only inputs that a parent component passes to a child component
- event handler: functions triggered  (onClick, onChange, onSubmit are React event props)
- state: data a component remembers between renders (useState)
    - useState returns [currentState, functionToUpdateState]
    - useState takes in the initial value as an argument
    - useState has an optional generic for the input type for functionToUpdateState
- useEffect: run code after rendering (keep React functions based purely on props + state)
- controlled forms (?)
- useEffect (?)
- context: shared application state (?)

api: 
- match the backend and create 1 file per router
- useful to have a low-level apiClient.ts for retries, auth etc.

Other tech stacks:
- react/svelte/vue: UI libraries
- vite: client-side build tool
- next.js/remix/tanstack start: full-stack frontend framework
- generally you choose either a client-side build tool (like Vite) or a full-stack framework (like Next.js or Remix) as the foundation of your app
- next.js is built on top of react