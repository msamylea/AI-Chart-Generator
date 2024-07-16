## Syntax

The idea behind syntax is that a user types sankey-beta keyword first, then pastes raw CSV below and get the result.
Do not use more than 10 lines total for source,target,value.

It implements CSV standard as described here with subtle differences:

CSV must contain 3 columns only
It is allowed to have empty lines without comma separators for visual purposes
Basic
It is implied that 3 columns inside CSV should represent source, target and value accordingly

```mermaid-example
sankey-beta

%% source,target,value
Electricity grid,Over generation / exports,104.453
Electricity grid,Heating and cooling - homes,113.726
Electricity grid,H2 conversion,27.14

```

Empty Lines
CSV does not support empty lines without comma delimiters by default. But you can add them if needed

```mermaid-example
sankey-beta

Bio-conversion,Losses,26.862

Bio-conversion,Solid,280.322

Bio-conversion,Gas,81.144


```

Commas
If you need to have a comma, wrap it in double quotes

```mermaid-example
sankey-beta

Pumped heat,"Heating and cooling, homes",193.026
Pumped heat,"Heating and cooling, commercial",70.672

```



Double Quotes
If you need to have double quote, put a pair of them inside quoted string:

```mermaid-example
sankey-beta

Pumped heat,"Heating and cooling, ""homes""",193.026
Pumped heat,"Heating and cooling, ""commercial""",70.672


```
