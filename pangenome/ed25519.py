"""Ed25519 — RFC 8032, pure stdlib, extended twisted Edwards coordinates.

Vendored deliberately. The organism has zero third-party dependencies: its
metabolism must be cheap enough to run forever on a free scheduled runner, and
every dependency is an attack surface on the one component that must never be
compromised — the signature check that gates capability integration.

Points are held as (X, Y, Z, T) with x = X/Z, y = Y/Z, T = XY/Z. The naive
affine formulas need a modular inversion per group operation, which is a full
modexp; extended coordinates defer all of that to a single inversion at the end.
It is roughly two orders of magnitude faster, which is the difference between a
simulation that runs and one that does not.

Formulas: add-2008-hwcd-3 and dbl-2008-hwcd (Hisil–Wong–Carter–Dawson), the
a = -1 specialisation Ed25519 uses.
"""

import hashlib
import os

_b = 256
_q = 2**255 - 19
_l = 2**252 + 27742317777372353535851937790883648493


def _H(m: bytes) -> bytes:
    return hashlib.sha512(m).digest()


def _inv(x: int) -> int:
    return pow(x, _q - 2, _q)


_d = -121665 * _inv(121666) % _q
_d2 = 2 * _d % _q
_I = pow(2, (_q - 1) // 4, _q)


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * _inv(_d * y * y + 1)
    x = pow(xx, (_q + 3) // 8, _q)
    if (x * x - xx) % _q != 0:
        x = (x * _I) % _q
    if x % 2 != 0:
        x = _q - x
    return x


_By = 4 * _inv(5) % _q
_Bx = _xrecover(_By)
_B = (_Bx, _By, 1, _Bx * _By % _q)
_IDENT = (0, 1, 1, 0)


def _add(P, Q):
    X1, Y1, Z1, T1 = P
    X2, Y2, Z2, T2 = Q
    A = (Y1 - X1) * (Y2 - X2) % _q
    B = (Y1 + X1) * (Y2 + X2) % _q
    C = T1 * _d2 * T2 % _q
    D = 2 * Z1 * Z2 % _q
    E = (B - A) % _q
    F = (D - C) % _q
    G = (D + C) % _q
    Hh = (B + A) % _q
    return (E * F % _q, G * Hh % _q, F * G % _q, E * Hh % _q)


def _double(P):
    X1, Y1, Z1, _ = P
    A = X1 * X1 % _q
    B = Y1 * Y1 % _q
    C = 2 * Z1 * Z1 % _q
    D = -A % _q
    E = ((X1 + Y1) * (X1 + Y1) - A - B) % _q
    G = (D + B) % _q
    F = (G - C) % _q
    Hh = (D - B) % _q
    return (E * F % _q, G * Hh % _q, F * G % _q, E * Hh % _q)


def _scalarmult(P, e: int):
    """Double-and-add over the bits of e, most significant first."""
    if e == 0:
        return _IDENT
    R = _IDENT
    for bit in bin(e)[2:]:
        R = _double(R)
        if bit == "1":
            R = _add(R, P)
    return R


def _affine(P):
    X, Y, Z, _ = P
    zi = _inv(Z)
    return (X * zi % _q, Y * zi % _q)


def _equal(P, Q) -> bool:
    """Compare projectively — cross-multiply rather than invert twice."""
    X1, Y1, Z1, _ = P
    X2, Y2, Z2, _ = Q
    return (X1 * Z2 - X2 * Z1) % _q == 0 and (Y1 * Z2 - Y2 * Z1) % _q == 0


def _encodepoint(P) -> bytes:
    x, y = _affine(P)
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def _decodepoint(s: bytes):
    v = int.from_bytes(s, "little")
    y = v & ((1 << 255) - 1)
    if y >= _q:
        raise ValueError("y out of range")
    x = _xrecover(y)
    if x & 1 != (v >> 255):
        x = _q - x
    if (-x * x + y * y - 1 - _d * x * x * y * y) % _q != 0:
        raise ValueError("point is not on curve")
    return (x, y, 1, x * y % _q)


def _bit(h: bytes, i: int) -> int:
    return (h[i // 8] >> (i % 8)) & 1


def _secret_scalar(h: bytes) -> int:
    return 2 ** (_b - 2) + sum(2**i * _bit(h, i) for i in range(3, _b - 2))


def _Hint(m: bytes) -> int:
    return int.from_bytes(_H(m), "little") % _l


# --- public API -------------------------------------------------------------

def keygen() -> tuple[bytes, bytes]:
    """Return (secret_key_32, public_key_32)."""
    sk = os.urandom(32)
    return sk, publickey(sk)


def publickey(sk: bytes) -> bytes:
    return _encodepoint(_scalarmult(_B, _secret_scalar(_H(sk))))


def sign(msg: bytes, sk: bytes, pk: bytes) -> bytes:
    h = _H(sk)
    a = _secret_scalar(h)
    r = _Hint(h[32:64] + msg)
    R = _scalarmult(_B, r)
    Renc = _encodepoint(R)
    S = (r + _Hint(Renc + pk + msg) * a) % _l
    return Renc + S.to_bytes(32, "little")


def verify(sig: bytes, msg: bytes, pk: bytes) -> bool:
    """Never raises. A malformed signature is an invalid signature."""
    try:
        if len(sig) != 64 or len(pk) != 32:
            return False
        S = int.from_bytes(sig[32:], "little")
        if S >= _l:
            return False
        R = _decodepoint(sig[:32])
        A = _decodepoint(pk)
        h = _Hint(sig[:32] + pk + msg)
        return _equal(_scalarmult(_B, S), _add(R, _scalarmult(A, h)))
    except Exception:
        return False
