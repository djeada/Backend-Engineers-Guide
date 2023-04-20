## Stateful vs Stateless

When making applications, think about if they should be stateful or stateless. These words are about how an application handles data.

## Stateful Applications

Stateful applications remember past events to respond to new interactions.

### Pros of Stateful Applications

- Easier to program since they don't need extra info to understand a request.
- Can hold onto complex states.
- Good at handling complex workflows.

### Cons of Stateful Applications

- Harder to scale since all instances need the same info.
- Prone to crashes if there's an error because it can't recover the past state.

## Stateless Applications

Stateless applications don't remember past events when responding to new interactions. Each request is separate.

### Pros of Stateless Applications

- Good at handling lots of traffic since each request is separate and doesn't need past context.
- Easier to scale since instances don't rely on the same info.
- Can recover from errors more easily since there's no past state to keep.

### Cons of Stateless Applications

- Can't hold onto complex states, causing problems for some workflows.
- Harder to program since each request needs enough info to understand its context.

## Common Issues

Whether an app is stateful or stateless, watch out for these issues:

- Network connections, needed for most modern applications.
- Changing the filesystem, often needed to save or get data.
- Database tasks, important for most applications.

When choosing between stateful or stateless, think about the use case and expected traffic. Stateless applications are better for high-traffic situations, while stateful applications are better for complex workflows that need to remember past context.
