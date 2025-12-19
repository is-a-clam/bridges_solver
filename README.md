# Solver for Bridges / Hashiwokakero

This is a generator and solver for the logic puzzle game Bridges (also known as Hashiwokakero).

To run the demo, first ensure you have Python 3.9+ and install the required packages:

```shell
python -m pip install -r requirements.txt
```

Then run the demo:

```shell
./demo
```

## Generator Algorithm

Repeat while the board can be expanded and the number of islands remains below the minimum threshold:

1. Select a random expandable island
2. Select a random available bridge direction, thickness, and length
3. Verify the new island is not adjacent to any existing island
4. Construct the new bridge and island

Occasionally, the generated board may leave an outer row or column completely empty. If this happens, a new board will be generated from scratch.

The algorithm supports multiple difficulty settings: easy, medium, hard, and extreme. Higher difficulties increase the desired island density and raise the odds of a single bridge over a double bridge, making deduction strategies less effective. On the extreme setting, bridge lengths are further skewed toward shorter spans to encourage denser boards.

## Solver Algorithm

The solver formulates an integer linear program (ILP) based on the given board to solve the puzzle.

**Sets:**

- $N$ : set of all islands
- $E$ : set of all potential bridges
- $C$ : set of all potential crossing bridges

**Variables:**

- $r_i$ : degree of node $i$
- $b_{i,j} \in \{0,1,2\}$ : bridge count
- $y_{i,j} \in \{0,1\}$ : bridge existence indicator
- $f_{i,j} \ge 0$ : flow from node $i$ to $j$

**Constraints:**

- minimize $\sum_{i,j} b_{i,j}$
- island degree: $\forall i \in N$ : $\sum_{j \in N: (i,j) \in E} b_{i,j} = r_i$
- bridge existence: $\forall (i,j) \in E$ : $y_{i,j} \le b_{i,j} \le 2\,y_{i,j}$
- no crossing: $\forall ((i,j),(k,l)) \in C$ : $y_{i,j} + y_{k,l} \le 1$
- flow conservation: $\forall i \in N$ : $\sum_{j} f_{i,j} - \sum_{j} f_{j,i} = \begin{cases} |N|-1 & \text{if } i = 0 \\ -1 & \text{otherwise} \end{cases}$
- flow capacity: $\forall (i,j) \in E$ : $f_{i,j} + f_{j,i} \le (|N| - 1)\, y_{i,j}$

The flow conservation and flow capacity constraints ensure that all islands and bridges form a single connected graph.
