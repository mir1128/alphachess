

###  ucb函数



蒙特卡洛树搜索（MCTS）中的UCB（Upper Confidence Bound）函数通常用于在树策略阶段平衡探索和利用。最常用的UCB函数是UCB1，它源自多臂老虎机问题。UCB1公式如下：
$$
UCB1 = \frac{X_i}{N_i} + c \sqrt{\frac{2 \ln N}{N_i}}
$$


其中***X_i***表示节点 ***i*** 的累计奖励，***N_i***表示节点***i***的访问次数，***N***表示父节点的访问次数，***c***是一个用于调整探索与利用平衡的常数。

------

> 这里是一个使用蒙特卡洛树搜索（MCTS）和UCB1函数的简化示例。在这个例子中，我们将实现一个简单的模拟决策问题，包括一个根节点和两个子节点。我们将使用MCTS和UCB1来确定哪个子节点具有更高的潜在价值。
>
> 首先，我们定义一个简单的`Node`类来表示树中的节点：
>
> ```python
> class Node:
>     def __init__(self, parent=None):
>         self.parent = parent
>         self.total_reward = 0
>         self.visit_count = 0
>         self.children = []
> ```
>
> 接下来，我们实现UCB1函数：
>
> ```python
> import math
> 
> def ucb1(node, c=1.0):
>     exploitation = node.total_reward / node.visit_count if node.visit_count > 0 else 0
>     exploration = math.sqrt(2*math.log(node.parent.visit_count)/node.visit_count) if node.visit_count > 0 else float("inf")
>     return exploitation + c * exploration
> ```
>
> 现在，我们可以创建一个简化的MCTS过程。在这个例子中，我们将假设每个子节点的奖励是已知的，但在实际应用中，你需要通过模拟游戏或其他方法来估计奖励。
>
> ```python
> # Create the root node and two child nodes
> root = Node()
> child1 = Node(parent=root)
> child2 = Node(parent=root)
> root.children = [child1, child2]
> 
> # Set the known rewards for each child node
> child1.total_reward = 100
> child1.visit_count = 50
> child2.total_reward = 120
> child2.visit_count = 60
> 
> # Calculate the UCB1 values for each child node
> ucb1_child1 = ucb1(child1)
> ucb1_child2 = ucb1(child2)
> 
> print("UCB1 value for child 1:", ucb1_child1)
> print("UCB1 value for child 2:", ucb1_child2)
> 
> # Choose the child node with the highest UCB1 value
> best_child = max(root.children, key=ucb1)
> print("Best child:", best_child)
> ```
>
> 在这个简化示例中，我们计算了两个子节点的UCB1值，并选择了UCB1值最高的子节点。在实际应用中，MCTS将对树进行多次完整的遍历，包括选择、扩展、模拟和反向传播阶段，以找到具有最高潜在价值的子节点。



对于UCB1函数的感性理解：

在 UCB1（Upper Confidence Bound 1）公式中，exploration 部分的目的是平衡探索和利用。这部分的公式来源于 Hoeffding 不等式的一种变形，它试图在不确定性较大的情况下，为每个节点提供一个置信上界。

`2 * ln(N) / N_i` 这部分的数学原理来自于多臂赌博机问题中的 Hoeffding 不等式。在多臂赌博机问题中，我们致力于找到一个策略，在给定时间内使得总收益最大化。我们希望尽可能多地尝试那些可能性较大的手臂，同时尽量减少尝试那些可能性较小的手臂。为了找到这样的策略，我们需要在探索（尝试新手臂）和利用（利用已知手臂）之间找到一个平衡。

这个公式的直观解释是：

- `N` 代表父节点的总访问次数。随着父节点的访问次数增加，`ln(N)` 会增加，但增长速度会逐渐减缓。这意味着随着时间的推移，我们越来越倾向于利用已知手臂，而不是继续探索。
- `N_i` 代表当前节点的访问次数。当一个节点被访问得越多，它的不确定性就越小。这意味着我们应该更多地关注那些访问次数较少的节点，以便更好地了解它们的潜在价值。

将这两部分相除，我们可以得到一个度量不确定性的值。但是，`2 * ln(N) / N_i` 这个值可能会随着时间的推移变得非常大。为了将其缩放到一个合适的范围，我们对其开平方。这可以确保 exploration 部分不会过大，从而影响 exploitation 部分。

总之，UCB1 公式的 exploration 部分试图在探索和利用之间找到一个平衡。它基于 Hoeffding 不等式来度量每个节点的不确定性，并通过开平方将其缩放到合适的范围。这种方法在多臂赌博机问题和蒙特卡洛树搜索等领域已经被证明是非常有效的。



上面提到了Hoeffding不等式，以下是与Hoeffding不等式有关的内容：

Hoeffding不等式是概率论中的一个重要结论，它提供了一种界定独立随机变量之和与其期望之间差距的概率界限。该不等式由Wassily Hoeffding于1963年提出，主要用于理论分析和概率估计等领域。

考虑一组独立随机变量$X_1, X_2, \dots, X_n$，其中每个随机变量$X_i$满足$X_i \in [a_i, b_i]$，并且$\mathbb{E}[X_i] = \mu_i$。令$S_n = \sum_{i=1}^{n} X_i$表示这些随机变量的和，以及$\bar{X}_n = \frac{1}{n} S_n$表示它们的平均值。Hoeffding不等式给出了$S_n$或$\bar{X}_n$与其期望值之间差距的概率界限。

Hoeffding不等式的具体形式如下：

对于任意$t > 0$，我们有
$$
\mathbb{P}\left(S_n - \mathbb{E}[S_n] \geq t\right) \leq \exp\left(-\frac{2t^2}{\sum_{i=1}^{n}(b_i - a_i)^2}\right)
$$
同时，
$$
\mathbb{P}\left(S_n - \mathbb{E}[S_n] \leq -t\right) \leq \exp\left(-\frac{2t^2}{\sum_{i=1}^{n}(b_i - a_i)^2}\right)
$$
这两个式子分别给出了$S_n$比其期望值大（或小）至少$t$的概率的上界。

将这个不等式应用于均值$\bar{X}_n$，我们可以得到：
$$
\mathbb{P}\left(\bar{X}_n - \mathbb{E}[\bar{X}*n] \geq t\right) \leq \exp\left(-\frac{2nt^2}{\sum*{i=1}^{n}(b_i - a_i)^2}\right)
$$
以及
$$
\mathbb{P}\left(\bar{X}_n - \mathbb{E}[\bar{X}*n] \leq -t\right) \leq \exp\left(-\frac{2nt^2}{\sum*{i=1}^{n}(b_i - a_i)^2}\right)
$$
Hoeffding不等式在许多领域都有着广泛的应用，例如机器学习、统计学和信息论等。其中一个典型的应用是在机器学习中分析算法的泛化性能，通过控制训练误差与测试误差之间的差距概率。







------

虽然UCB1是最常用的UCB函数，但实际上可以根据问题和应用场景设计不同的UCB函数。例如，以下是一些变种：

1. **UCB1-Tuned**：UCB1-Tuned是UCB1的一个改进，它考虑了每个节点的平均奖励的方差。修改后的公式如下：
   $$
   UCB1\text{-}Tuned = \frac{X_i}{N_i} + \sqrt{\frac{\ln N}{N_i} \min \left( \frac{1}{4}, V_i(N_i) \right)}
   $$
   
   其中$V_i(N_i)$是节点$i$的奖励方差的估计。
   
2. **UCB-V**：UCB-V是另一个考虑奖励方差的UCB公式。它的计算公式如下：

   $$
   UCB\text{-}V = \frac{X_i}{N_i} + c \sqrt{\frac{2 V_i(N_i) \ln N}{N_i}} + \frac{3 \ln N}{2 N_i}
   $$

3. **Hoeffding Upper Confidence Bound (H-UCB)**：H-UCB利用霍夫丁不等式（Hoeffding's inequality）来调整上置信界。H-UCB公式如下：

   $$
   H\text{-}UCB = \frac{X_i}{N_i} + \sqrt{\frac{2 \ln N}{N_i} \frac{R^2}{4}}
   $$

   其中$R$是奖励的最大可能范围。

4. **Bayesian Upper Confidence Bound (Bayes-UCB)**：Bayes-UCB基于贝叶斯思想，使用后验概率分布来计算置信界。根据问题的具体设置，Bayes-UCB的计算方法会有所不同。