# Mathematical Functions

Derived mathematical functions that can be calculated using BASIC-80's intrinsic functions.

## Trigonometric Functions

### Basic Trigonometric Functions

BASIC-80 provides: [SIN](../functions/sin.md), [COS](../functions/cos.md), [TAN](../functions/tan.md), [ATN](../functions/atn.md)

### Derived Trigonometric Functions

| Function | BASIC-80 Equivalent |
|----------|---------------------|
| **Secant** | `SEC(X) = 1/COS(X)` |
| **Cosecant** | `CSC(X) = 1/SIN(X)` |
| **Cotangent** | `COT(X) = 1/TAN(X)` |

### Inverse Trigonometric Functions

| Function | BASIC-80 Equivalent |
|----------|---------------------|
| **Inverse Sine** | `ARCSIN(X) = ATN(X/SQR(-X*X+1))` |
| **Inverse Cosine** | `ARCCOS(X) = -ATN(X/SQR(-X*X+1)) + 1.5708` |
| **Inverse Secant** | `ARCSEC(X) = ATN(X/SQR(X*X-1)) + SGN(SGN(X)-1) * 1.5708` |
| **Inverse Cosecant** | `ARCCSC(X) = ATN(X/SQR(X*X-1)) + (SGN(X)-1) * 1.5708` |
| **Inverse Cotangent** | `ARCCOT(X) = ATN(X) + 1.5708` |

## Hyperbolic Functions

### Direct Hyperbolic Functions

| Function | BASIC-80 Equivalent |
|----------|---------------------|
| **Hyperbolic Sine** | `SINH(X) = (EXP(X) - EXP(-X)) / 2` |
| **Hyperbolic Cosine** | `COSH(X) = (EXP(X) + EXP(-X)) / 2` |
| **Hyperbolic Tangent** | `TANH(X) = (EXP(-X) / (EXP(X) + EXP(-X))) * 2 + 1` |
| **Hyperbolic Secant** | `SECH(X) = 2 / (EXP(X) + EXP(-X))` |
| **Hyperbolic Cosecant** | `CSCH(X) = 2 / (EXP(X) - EXP(-X))` |
| **Hyperbolic Cotangent** | `COTH(X) = (EXP(-X) / (EXP(X) - EXP(-X))) * 2 + 1` |

### Inverse Hyperbolic Functions

| Function | BASIC-80 Equivalent |
|----------|---------------------|
| **Inverse Hyperbolic Sine** | `ARCSINH(X) = LOG(X + SQR(X*X + 1))` |
| **Inverse Hyperbolic Cosine** | `ARCCOSH(X) = LOG(X + SQR(X*X - 1))` |
| **Inverse Hyperbolic Tangent** | `ARCTANH(X) = LOG((1 + X) / (1 - X)) / 2` |
| **Inverse Hyperbolic Secant** | `ARCSECH(X) = LOG((SQR(-X*X + 1) + 1) / X)` |
| **Inverse Hyperbolic Cosecant** | `ARCCSCH(X) = LOG((SGN(X) * SQR(X*X + 1) + 1) / X)` |
| **Inverse Hyperbolic Cotangent** | `ARCCOTH(X) = LOG((X + 1) / (X - 1)) / 2` |

## Example Usage

### Computing Inverse Sine

```basic
10 REM Inverse sine function
20 DEF FNARCSIN(X) = ATN(X/SQR(-X*X+1))
30 INPUT "Enter value (-1 to 1)"; V
40 PRINT "ARCSIN("; V; ") = "; FNARCSIN(V)
```

### Computing Hyperbolic Sine

```basic
10 REM Hyperbolic sine function
20 DEF FNSINH(X) = (EXP(X) - EXP(-X)) / 2
30 INPUT "Enter value"; V
40 PRINT "SINH("; V; ") = "; FNSINH(V)
```

### Computing Secant

```basic
10 REM Secant function
20 DEF FNSEC(X) = 1 / COS(X)
30 INPUT "Enter angle in radians"; A
40 PRINT "SEC("; A; ") = "; FNSEC(A)
```

## Constants

### Important Mathematical Constants

```basic
PI = 3.141592653589793   ' Use ATN(1) * 4 for pi
E = 2.718281828459045    ' Use EXP(1) for e
```

### Computing Pi

```basic
10 REM Calculate PI
20 PI = ATN(1) * 4
30 PRINT "PI = "; PI
```

## Related Functions

### Built-in Mathematical Functions

- [SIN](../functions/sin.md) - Sine (in radians)
- [COS](../functions/cos.md) - Cosine (in radians)
- [TAN](../functions/tan.md) - Tangent (in radians)
- [ATN](../functions/atn.md) - Arctangent (in radians)
- [EXP](../functions/exp.md) - Exponential (e^x)
- [LOG](../functions/log.md) - Natural logarithm
- [SQR](../functions/sqr.md) - Square root
- [ABS](../functions/abs.md) - Absolute value
- [SGN](../functions/sgn.md) - Sign (-1, 0, or 1)

### Defining Custom Functions

Use [DEF FN](../statements/def-fn.md) to define your own mathematical functions:

```basic
10 DEF FNHYPOT(X, Y) = SQR(X*X + Y*Y)
20 PRINT "Hypotenuse of 3,4 triangle = "; FNHYPOT(3, 4)
```

## See Also

- [DEF FN Statement](../statements/def-fn.md) - Define user functions
- [Functions Index](../functions/index.md) - All built-in functions
- [Operators](../operators.md) - Arithmetic operators
