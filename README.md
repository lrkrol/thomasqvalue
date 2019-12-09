
# thomasqvalue

**thomasqvalue** implements a number of functions taken from and related to the 1963 publication by Thomas

* H. B. G. Thomas (1963), Communication theory and the constellation hypothesis of calculation, *Quarterly Journal of Experimental Psychology*, 15:3, 173-191, doi: 10.1080/17470216308416323
    
in which he postulates that a certain Q-value can represent the information requirement of a given calculation. The proposed formula for calculating such Q-values breaks a calculation down into single-digit sub-calculations, and takes into account both the number of these single-digit calculations, and the amount to which information is carried over to subsequent sub-calculations.

```python
import thomasqvalue as tqv

# Q-value for 345 + 9585
q = tqv.q_addition(345, 9585)

# Q-value for 6 * 7895
q = tqv.q_multiplication(6, 7895)

# Q-value for 793 - 645
q = tqv.q_subtraction(793, 645)

# get random numbers and corresponding Q-value for an addition calculation
# with numbers between 200 and 999, and a Q-value between 3.75 and 4.25
[n1, n2, q] = tqv.get_calculation_addition(3.75, 4.25, 200, 999)

# get random numbers and corresponding Q-value for a multiplication calculation
# with a multiplicand between 1000 and 9999, and a Q-value between 5.975 and 6.025
[x, m, q] = tqv.get_calculation_multiplication(5.975, 6.025, 1000, 9999)

# get random numbers and corresponding Q-value for a subtraction calculation
# with numbers between 75 and 650, and a Q-value between 2.5 and 4
[x, m, q] = tqv.get_calculation_subtraction(2.5, 4, 75, 650)
```

This implementation uses the "short" addition constellations suggested by Thomas, and generalises the proposal made in the original paper by allowing digits to be zero, which also means it can accept two numbers of different length. Here, any calculation that involves only one non-zero digit is given a Q-value of 0, taking into account the possibility of a previously carried 1. This extends the range of possible Q-values down towards 0, and means that e.g. `Q[10 + 1] = 0`, whereas `Q[11 + 1] = 0.6`. Although I believe this to be in line with Thomas' argumentation, it may not be entirely in the original spirit -- Thomas himself did exclude all zeros, so use with caution.

The subtraction procedure is implemented analogous to the addition procedure, where the short constellation leaves out the final resulting digit, making e.g. the first constellation for `11-2` to be `(1, 2, abs(1-2))`. This appears to be what Thomas intended: for "... one-stage sums ... in which the answer is not equal to the sum of the problem-digits, ... it is the answer which should be omitted ..." Note that this causes an invariance with respect to `d2` for sub-calculations that produce no carry, and an invariance with respect to `d1` when a carry is produced. Because of this, I am personally not entirely convinced this is correct, but Thomas does not discuss this. Subtraction has also been extended to accept zeros, where a Q-value of 0 is returned for each sub-calculation that subtracts 0, including the potential carry. 

The multiplication procedure has not been generalised and still requires a one-digit number for the first part of the calculation. Presumably, generalisation requires a combination of multiplication and addition, but this has not been discussed in the original paper.

Note that the probability of success of the get_calculation functions depends on all of the given arguments: a small allowed range of Q-values, a mismatched range of allowed numbers, and a small amount of trials may all result in failure even though calculations in the requested range do exist.
