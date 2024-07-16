## Syntax

At its core, a block diagram consists of blocks representing different entities or components. In Mermaid, these blocks are easily created using simple text labels. The most basic form of a block diagram can be a series of blocks without any connectors.

```mermaid-example
block-beta
  a b c

```

```mermaid-example
block-beta
  columns 3
  a b c d

```

```mermaid-example
block-beta
  columns 3
  a["A label"] b:2 c:2 d

```

```mermaid-example
block-beta
    block
      D
    end
    A["A: I am a wide one"]

```

```mermaid-example
block-beta
  columns 3
  a:3
  block:group1:2
    columns 2
    h i j k
  end
  g
  block:group2:3
    %% columns auto (default)
    l m n o p q r
  end
```

To create a block with round edges, which can be used to represent a softer or more flexible component, surround the text with ( )

A stadium-shaped block, resembling an elongated circle, can be used for components that are process-oriented, and use ([ ])

For representing subroutines or contained processes, a block with double vertical lines is useful [[ ]]

The cylindrical shape is ideal for representing databases or storage components [( )]

A circle can be used for centralized or pivotal components (( ))

Rhombus: { }

Hexagon: {{ }}

A simple link with an arrow can be created to show direction or flow from one block to another -->

Double Circle: ((( )))
```mermaid-example
block-beta
    id1("This is the text in the box")

```


```mermaid-example
block-beta
    id1(["This is the text in the box"])

```

```mermaid-example
block-beta
columns 1
  db(("DB"))
  blockArrowId6<["&nbsp;&nbsp;&nbsp;"]>(down)
  block:ID
    A
    B["A wide one in the middle"]
    C
  end
  space
  D
  ID --> D
  C --> D
  style B fill:#939,stroke:#333,stroke-width:4px

```