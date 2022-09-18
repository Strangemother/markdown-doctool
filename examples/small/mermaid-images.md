# Mermaids

A mermaid diagram, using the plugin `md-mermaid` fish tails syntax:

    ​~~~mermaid
    ...
    ​~~~

​~~~mermaid
graph TD
A[Client] -->|tcp_123| B
B(Load Balancer)
B -->|tcp_456| C[Server1]
B -->|tcp_456| D[Server2]
​~~~

An `erDiagram` type graph, using the backtick "\`" syntax:

    ```mermaid
    ...
    ```

```mermaid
  erDiagram

    CUSTOMER }|..|{ DELIVERY-ADDRESS : has
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER ||--o{ INVOICE : "liable for"
    DELIVERY-ADDRESS ||--o{ ORDER : receives
    INVOICE ||--|{ ORDER : covers
    ORDER ||--|{ ORDER-ITEM : includes
    PRODUCT-CATEGORY ||--|{ PRODUCT : contains
    PRODUCT ||--o{ ORDER-ITEM : "ordered in"
```

## HTML class Include

You can apply a mermaid main using the html `div` with a class of `.mermaid`:

    <div class="mermaid">
        ...
    </div>

<div class="mermaid">
    graph TD
    A[Client] --> B[Load Balancer]
    B --> C[Server1]
    B --> D[Server2]
</div>


## Sequence Diagram

An example of a `sequenceDiagram` using the backtick "\`" syntax:

    ```mermaid
    ...
    ```

```mermaid
sequenceDiagram
  autonumber
  par Action 1
    Alice->>John: Hello John, how are you?
  and Action 2
    Alice->>Bob: Hello Bob, how are you?
  end
  Alice->>+John: Hello John, how are you?
  Alice->>+John: John, can you hear me?
  John-->>-Alice: Hi Alice, I can hear you!
  Note right of John: John is perceptive
  John-->>-Alice: I feel great!
      loop Every minute
        John-->Alice: Great!
    end
```


## Graph Diagram

A graph using the fish-tail syntax:

    ​~~~mermaid
    ​~~~

​~~~mermaid
graph TB
D --> E
E --> F
​~~~


​~~~mermaid
graph TD
  A[Christmas] -->|Get money| B(Go shopping)
  B --> C{Let me think}
  B --> G[/Another/]
  C ==>|One| D[Laptop]
  C -->|Two| E[iPhone]
  C -->|Three| F[fa:fa-car Car]
  subgraph section
    C
    D
    E
    F
    G
  end
​~~~
