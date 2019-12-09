#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
thomasqvalue

Copyright 2019 Laurens R Krol
    Team PhyPA, Biological Psychology and Neuroergonomics,
    Technische Universität Berlin
    lrkrol.com
    
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
thomasqvalue implements a number of functions taken from and related to the
1963 publication by Thomas

    H. B. G. Thomas (1963), Communication theory and the constellation
    hypothesis of calculation, Quarterly Journal of Experimental Psychology,
    15:3, 173-191, doi: 10.1080/17470216308416323
    
in which he postulates that a certain Q-value can represent the information
requirement of a given calculation. The proposed formula for calculating such
Q-values breaks a calculation down into single-digit sub-calculations, and
takes into account both the number of these single-digit calculations, and the
amount to which information is carried over to subsequent sub-calculations.

This implementation uses the "short" addition constellations suggested by
Thomas, and generalises the proposal made in the original paper by allowing
digits to be zero, which also means it can accept two numbers of different
length. Here, any calculation that involves only one non-zero digit is given
a Q-value of 0, taking into account the possibility of a previously carried 1.
This extends the range of possible Q-values down towards 0, and means that
e.g. Q[10 + 1] = 0, whereas Q[11 + 1] = 0.6. Although I believe this to be in
line with Thomas' argumentation, it may not be entirely in the original
spirit -- Thomas himself did exclude all zeros, so use with caution.

The subtraction procedure is implemented analogous to the addition procedure,
where the short constellation leaves out the final resulting digit, making
e.g. the first constellation for `11-2` to be `(1, 2, abs(1-2))`. This
appears to be what Thomas intended: for "... one-stage sums ... in which the
answer is not equal to the sum of the problem-digits, ... it is the answer
which should be omitted ..." Note that this causes an invariance with respect
to `d2` for sub-calculations that produce no carry, and an invariance with
respect to `d1` when a carry is produced. Because of this, I am personally not
entirely convinced this is correct, but Thomas does not discuss this.
Subtraction has also been extended to accept zeros, where a Q-value of 0 is
returned for each sub-calculation that subtracts 0, including the potential
carry. 

The multiplication procedure has not been generalised and still requires a
one-digit number for the first part of the calculation. Presumably,
generalisation requires a combination of multiplication and addition, but
this has not been discussed in the original paper.

Note that the probability of success of the get_calculation functions depends
on all of the given arguments: a small allowed range of Q-values, a mismatched
range of allowed numbers, and a small amount of trials may all result in
failure even though calculations in the requested range do exist.
"""

"""
2019-12-09 0.2.0 lrk
  - q_addition now returns None for invalid input
  - Added subtraction functions
2019-12-05 0.1.1 lrk
  - Made get_calculation functions return list of Nones instead of single None
2019-12-04 0.1.0 First version
"""


from math import log10
from random import randint


def q_addition(n1, n2):
    """ returns Q[n1+n2]
        for n1 > 0 and n2 > 0,
        otherwise, returns None """
        
    if not (n1 > 0 and n2 > 0): return None
        
    # converting to string for easier digit iteration and zero-padding
    n1 = str(n1)
    n2 = str(n2)
    
    # zero-padding
    length = max(len(n1), len(n2))
    if len(n1) is not len(n2): 
        n1 = str(n1).zfill(length)
        n2 = str(n2).zfill(length)
    
    # calculating Q-value one digit pair at a time
    Q = 0
    carry = 0
    for d in range(length-1, -1, -1):
        d1 = int(n1[d])
        d2 = int(n2[d])
        
        if (d1 == 0 or d2 == 0) and carry == 0:
            # no calculation necessary
            pass
        elif d1 + d2 + carry < 10:
            # addition that does not produce a carry
            # constellation: d1, d2, d1+d2, and potential 1 from previous carry
            Q += log10(d1 + d2 + d1+d2 + carry)
            carry = 0
        else:
            # addition that does produce a carry
            # constellation: d1, d2, d1+d2, 10, and potential 1 from previous carry
            Q += log10(d1 + d2 + d1+d2 + 10 + carry)
            carry = 1
        
    return Q


def q_subtraction(n1, n2):
    """ returns Q[n1-n2],
        for n1 > 0, n2 > 0, and n2 < n1,
        otherwise, returns None """
        
    if not (n1 > 0 and n2 > 0 and n2 < n1): return None

    # converting to string for easier digit iteration and zero-padding
    n1 = str(n1)
    n2 = str(n2)
    
    # zero-padding
    length = max(len(n1), len(n2))
    if len(n1) is not len(n2): 
        n1 = str(n1).zfill(length)
        n2 = str(n2).zfill(length)
    
    # calculating Q-value one digit pair at a time
    Q = 0
    carry = 0
    for d in range(length-1, -1, -1):
        d1 = int(n1[d])
        d2 = int(n2[d])
        
        if d2 == 0 and carry == 0:
            # no calculation necessary
            pass
        elif d1 - d2 - carry >= 0:
            # subtraction that does not produce a carry
            # constellation: d1, d12 |d1-d2|, and potential 1 from previous carry
            Q += log10(d1 + d2 + abs(d1-d2) + carry)
            carry = 0
        elif d1 - d2 - carry < 0:
            # subtraction that does produce a carry
            # constellation: d1, d2, |d1-d2|, 10, and potential 1 from previous carry
            Q += log10(d1 + d2 + abs(d1-d2) + 10 + carry)
            carry = 1
        
    return Q
    
    
def q_multiplication(x, multiplicand):
    """ returns Q[x*multiplicand] for 2 <= x <= 9,
        otherwise, returns None """
    
    if x < 2 or x > 9: return None
    
    multiplicand = str(multiplicand)
    
    # calculating Q-value one digit of the multiplicand at a time
    Q = 0
    carry = 0
    for d in range(len(multiplicand)-1,-1,-1):
        m = int(multiplicand[d])
        
        if x * m + carry < 10:
            # multiplication that does not produce a carry
            # constellation: x, m, x*m, and potential remainder from previous carry
            Q += log10(x + m + x*m + carry)
            carry = 0
        elif d == 0 and carry == 0:
            # special case for final digit
            # constellation: x, m, x*m
            Q += log10(x + m + x*m)
        else:
            # multiplication that does produce a carry
                        
            intermediateproduct = x*m + carry
            remainder = intermediateproduct - intermediateproduct % 10
            newdigit = intermediateproduct % 10
                        
            if intermediateproduct % 10 == 0:
                # special case for multiplications of 10
                # constellation: x, m, x*m, potential remainder from previous carry, intermediate product
                Q += log10(x + m + x*m + carry + intermediateproduct)
            elif d == 0:
                # special case for final digit
                Q += log10(x + m + x*m + carry + intermediateproduct)
            elif carry > 0:
                # constellation: x, m, x*m, potential remainder from previous carry, intermediate product, current remainder, and final digit
                Q += log10(x + m + x*m + carry + intermediateproduct + remainder + newdigit)
            else:
                # constellation: x, m, x*m, current remainder, and final digit
                Q += log10(x + m + x*m + remainder + newdigit)
            
            carry = remainder / 10
        
    return Q
    
    
def get_calculation_addition(lower, upper, minint = 1, maxint = 999, ntrials = 20000):
    """ returns [n1, n2, q] where lower <= Q[n1+n2] <= upper,
        and minint <= n1 <= maxint, minint <= n2 <= maxint,
        and q = Q[n1+n2];
        otherwise, if no solution can be found within ntrials attempts,
        returns [None, None, None] """
    
    # trying to find a fitting calculation, otherwise returning None;
    for i in range(ntrials):
        n1 = randint(minint, maxint)
        n2 = randint(minint, maxint)
        if q_addition(n1, n2) >= lower and q_addition(n1, n2) <= upper:
            return [n1, n2, q_addition(n1, n2)]
    return [None, None, None]
    
    
def get_calculation_subtraction(lower, upper, minint = 1, maxint = 999, ntrials = 20000):
    """ returns [n1, n2, q] where lower <= Q[n1-n2] <= upper,
        and minint <= n1 <= maxint, minint <= n2 <= n1,
        and q = Q[n1-n2];
        otherwise, if no solution can be found within ntrials attempts,
        returns [None, None, None] """
    
    # trying to find a fitting calculation, otherwise returning None;
    for i in range(ntrials):
        n1 = randint(minint, maxint)
        n2 = randint(minint, n1)
        if q_subtraction(n1, n2) >= lower and q_subtraction(n1, n2) <= upper:
            return [n1, n2, q_subtraction(n1, n2)]
    return [None, None, None]
        
    
def get_calculation_multiplication(lower, upper, minint = 2, maxint = 9999, ntrials = 20000):
    """ returns [x, multiplicand, q] where lower <= Q[x*multiplicand] <= upper,
        and 2 <= x <= 9, minint <= multiplicand <= maxint,
        and q = Q[x*multiplicand];
        otherwise, if no solution can be found within ntrials attempts,
        returns [None, None, None] """
    
    # trying to find a fitting calculation, otherwise returning None;
    for i in range(ntrials):
        x = randint(2, 9)
        multiplicand = randint(minint, maxint)
        if q_multiplication(x, multiplicand) >= lower and q_multiplication(x, multiplicand) <= upper:
            return [x, multiplicand, q_multiplication(x, multiplicand)]
    return [None, None, None]


if __name__ == '__main__':
    print 'calculating Q[n1+n2]'
    n1 = int(raw_input('n1: ').strip())
    n2 = int(raw_input('n2: ').strip())

    print q_addition(n1, n2)
