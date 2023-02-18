# Stateful vs Stateless

When building applications, it's important to consider whether they should be stateful or stateless. These terms refer to how an application manages its data.

## Stateful Applications

Stateful applications are those that rely on the retention of previous interactions or events to determine how they respond to subsequent interactions. This means that these applications have a memory of past events and are able to use that information to make decisions.

### Advantages of Stateful Applications

- Easy to program since they do not require extra information to understand the context of a request.
- Able to retain complex states.
- Capable of handling complex workflows.

### Disadvantages of Stateful Applications

- Scaling can be difficult since a stateful application requires that all instances have the same information.
- In the event of an error, stateful applications can be prone to crashes since the system is unable to recover the previous state.

## Stateless Applications

Stateless applications are those that do not rely on any memory of previous interactions or events to determine how they respond to subsequent interactions. This means that each request is treated as an independent transaction.

### Advantages of Stateless Applications

- Able to handle high traffic since each request is independent and does not require any previous context.
- Easier to scale since each instance does not rely on the same information.
- In the event of an error, stateless applications can recover more easily since there is no previous state to maintain.

### Disadvantages of Stateless Applications

- Unable to retain complex states, which can be problematic for some workflows.
- More difficult to program since each request must contain enough information to understand the context of a request.

## Common Side Effects

Regardless of whether an application is stateful or stateless, there are common side effects that should be considered. These include:

- Network connections, which are required for most modern applications.
- Filesystem manipulation, which is often required to store or retrieve data.
- Database operations, which are essential for most applications.

When deciding whether an application should be stateful or stateless, it's important to consider the use case and the expected load. Stateless applications are generally better suited for high-traffic scenarios, while stateful applications are better suited for complex workflows that require the retention of previous context.
