"use strict";
(self.webpackChunkfrontend = self.webpackChunkfrontend || []).push([
  [792],
  {
    272: () => {
      function ne(e) {
        return "function" == typeof e;
      }
      function eo(e) {
        const n = e((r) => {
          Error.call(r), (r.stack = new Error().stack);
        });
        return (
          (n.prototype = Object.create(Error.prototype)),
          (n.prototype.constructor = n),
          n
        );
      }
      const Bs = eo(
        (e) =>
          function (n) {
            e(this),
              (this.message = n
                ? `${n.length} errors occurred during unsubscription:\n${n
                    .map((r, i) => `${i + 1}) ${r.toString()}`)
                    .join("\n  ")}`
                : ""),
              (this.name = "UnsubscriptionError"),
              (this.errors = n);
          },
      );
      function Fr(e, t) {
        if (e) {
          const n = e.indexOf(t);
          0 <= n && e.splice(n, 1);
        }
      }
      class je {
        constructor(t) {
          (this.initialTeardown = t),
            (this.closed = !1),
            (this._parentage = null),
            (this._finalizers = null);
        }
        unsubscribe() {
          let t;
          if (!this.closed) {
            this.closed = !0;
            const { _parentage: n } = this;
            if (n)
              if (((this._parentage = null), Array.isArray(n)))
                for (const o of n) o.remove(this);
              else n.remove(this);
            const { initialTeardown: r } = this;
            if (ne(r))
              try {
                r();
              } catch (o) {
                t = o instanceof Bs ? o.errors : [o];
              }
            const { _finalizers: i } = this;
            if (i) {
              this._finalizers = null;
              for (const o of i)
                try {
                  Ep(o);
                } catch (s) {
                  (t = t ?? []),
                    s instanceof Bs ? (t = [...t, ...s.errors]) : t.push(s);
                }
            }
            if (t) throw new Bs(t);
          }
        }
        add(t) {
          var n;
          if (t && t !== this)
            if (this.closed) Ep(t);
            else {
              if (t instanceof je) {
                if (t.closed || t._hasParent(this)) return;
                t._addParent(this);
              }
              (this._finalizers =
                null !== (n = this._finalizers) && void 0 !== n ? n : []).push(
                t,
              );
            }
        }
        _hasParent(t) {
          const { _parentage: n } = this;
          return n === t || (Array.isArray(n) && n.includes(t));
        }
        _addParent(t) {
          const { _parentage: n } = this;
          this._parentage = Array.isArray(n) ? (n.push(t), n) : n ? [n, t] : t;
        }
        _removeParent(t) {
          const { _parentage: n } = this;
          n === t ? (this._parentage = null) : Array.isArray(n) && Fr(n, t);
        }
        remove(t) {
          const { _finalizers: n } = this;
          n && Fr(n, t), t instanceof je && t._removeParent(this);
        }
      }
      je.EMPTY = (() => {
        const e = new je();
        return (e.closed = !0), e;
      })();
      const Dp = je.EMPTY;
      function wp(e) {
        return (
          e instanceof je ||
          (e && "closed" in e && ne(e.remove) && ne(e.add) && ne(e.unsubscribe))
        );
      }
      function Ep(e) {
        ne(e) ? e() : e.unsubscribe();
      }
      const rr = {
          onUnhandledError: null,
          onStoppedNotification: null,
          Promise: void 0,
          useDeprecatedSynchronousErrorHandling: !1,
          useDeprecatedNextContext: !1,
        },
        Vs = {
          setTimeout(e, t, ...n) {
            const { delegate: r } = Vs;
            return r?.setTimeout
              ? r.setTimeout(e, t, ...n)
              : setTimeout(e, t, ...n);
          },
          clearTimeout(e) {
            const { delegate: t } = Vs;
            return (t?.clearTimeout || clearTimeout)(e);
          },
          delegate: void 0,
        };
      function Cp(e) {
        Vs.setTimeout(() => {
          const { onUnhandledError: t } = rr;
          if (!t) throw e;
          t(e);
        });
      }
      function Tl() {}
      const TC = Al("C", void 0, void 0);
      function Al(e, t, n) {
        return { kind: e, value: t, error: n };
      }
      let ir = null;
      function $s(e) {
        if (rr.useDeprecatedSynchronousErrorHandling) {
          const t = !ir;
          if ((t && (ir = { errorThrown: !1, error: null }), e(), t)) {
            const { errorThrown: n, error: r } = ir;
            if (((ir = null), n)) throw r;
          }
        } else e();
      }
      class Nl extends je {
        constructor(t) {
          super(),
            (this.isStopped = !1),
            t
              ? ((this.destination = t), wp(t) && t.add(this))
              : (this.destination = FC);
        }
        static create(t, n, r) {
          return new to(t, n, r);
        }
        next(t) {
          this.isStopped
            ? Ol(
                (function NC(e) {
                  return Al("N", e, void 0);
                })(t),
                this,
              )
            : this._next(t);
        }
        error(t) {
          this.isStopped
            ? Ol(
                (function AC(e) {
                  return Al("E", void 0, e);
                })(t),
                this,
              )
            : ((this.isStopped = !0), this._error(t));
        }
        complete() {
          this.isStopped
            ? Ol(TC, this)
            : ((this.isStopped = !0), this._complete());
        }
        unsubscribe() {
          this.closed ||
            ((this.isStopped = !0),
            super.unsubscribe(),
            (this.destination = null));
        }
        _next(t) {
          this.destination.next(t);
        }
        _error(t) {
          try {
            this.destination.error(t);
          } finally {
            this.unsubscribe();
          }
        }
        _complete() {
          try {
            this.destination.complete();
          } finally {
            this.unsubscribe();
          }
        }
      }
      const OC = Function.prototype.bind;
      function Rl(e, t) {
        return OC.call(e, t);
      }
      class PC {
        constructor(t) {
          this.partialObserver = t;
        }
        next(t) {
          const { partialObserver: n } = this;
          if (n.next)
            try {
              n.next(t);
            } catch (r) {
              Us(r);
            }
        }
        error(t) {
          const { partialObserver: n } = this;
          if (n.error)
            try {
              n.error(t);
            } catch (r) {
              Us(r);
            }
          else Us(t);
        }
        complete() {
          const { partialObserver: t } = this;
          if (t.complete)
            try {
              t.complete();
            } catch (n) {
              Us(n);
            }
        }
      }
      class to extends Nl {
        constructor(t, n, r) {
          let i;
          if ((super(), ne(t) || !t))
            i = {
              next: t ?? void 0,
              error: n ?? void 0,
              complete: r ?? void 0,
            };
          else {
            let o;
            this && rr.useDeprecatedNextContext
              ? ((o = Object.create(t)),
                (o.unsubscribe = () => this.unsubscribe()),
                (i = {
                  next: t.next && Rl(t.next, o),
                  error: t.error && Rl(t.error, o),
                  complete: t.complete && Rl(t.complete, o),
                }))
              : (i = t);
          }
          this.destination = new PC(i);
        }
      }
      function Us(e) {
        rr.useDeprecatedSynchronousErrorHandling
          ? (function RC(e) {
              rr.useDeprecatedSynchronousErrorHandling &&
                ir &&
                ((ir.errorThrown = !0), (ir.error = e));
            })(e)
          : Cp(e);
      }
      function Ol(e, t) {
        const { onStoppedNotification: n } = rr;
        n && Vs.setTimeout(() => n(e, t));
      }
      const FC = {
          closed: !0,
          next: Tl,
          error: function kC(e) {
            throw e;
          },
          complete: Tl,
        },
        Pl =
          ("function" == typeof Symbol && Symbol.observable) || "@@observable";
      function kn(e) {
        return e;
      }
      function Ip(e) {
        return 0 === e.length
          ? kn
          : 1 === e.length
          ? e[0]
          : function (n) {
              return e.reduce((r, i) => i(r), n);
            };
      }
      let pe = (() => {
        class e {
          constructor(n) {
            n && (this._subscribe = n);
          }
          lift(n) {
            const r = new e();
            return (r.source = this), (r.operator = n), r;
          }
          subscribe(n, r, i) {
            const o = (function BC(e) {
              return (
                (e && e instanceof Nl) ||
                ((function jC(e) {
                  return e && ne(e.next) && ne(e.error) && ne(e.complete);
                })(e) &&
                  wp(e))
              );
            })(n)
              ? n
              : new to(n, r, i);
            return (
              $s(() => {
                const { operator: s, source: a } = this;
                o.add(
                  s
                    ? s.call(o, a)
                    : a
                    ? this._subscribe(o)
                    : this._trySubscribe(o),
                );
              }),
              o
            );
          }
          _trySubscribe(n) {
            try {
              return this._subscribe(n);
            } catch (r) {
              n.error(r);
            }
          }
          forEach(n, r) {
            return new (r = Mp(r))((i, o) => {
              const s = new to({
                next: (a) => {
                  try {
                    n(a);
                  } catch (c) {
                    o(c), s.unsubscribe();
                  }
                },
                error: o,
                complete: i,
              });
              this.subscribe(s);
            });
          }
          _subscribe(n) {
            var r;
            return null === (r = this.source) || void 0 === r
              ? void 0
              : r.subscribe(n);
          }
          [Pl]() {
            return this;
          }
          pipe(...n) {
            return Ip(n)(this);
          }
          toPromise(n) {
            return new (n = Mp(n))((r, i) => {
              let o;
              this.subscribe(
                (s) => (o = s),
                (s) => i(s),
                () => r(o),
              );
            });
          }
        }
        return (e.create = (t) => new e(t)), e;
      })();
      function Mp(e) {
        var t;
        return null !== (t = e ?? rr.Promise) && void 0 !== t ? t : Promise;
      }
      const VC = eo(
        (e) =>
          function () {
            e(this),
              (this.name = "ObjectUnsubscribedError"),
              (this.message = "object unsubscribed");
          },
      );
      let Te = (() => {
        class e extends pe {
          constructor() {
            super(),
              (this.closed = !1),
              (this.currentObservers = null),
              (this.observers = []),
              (this.isStopped = !1),
              (this.hasError = !1),
              (this.thrownError = null);
          }
          lift(n) {
            const r = new Sp(this, this);
            return (r.operator = n), r;
          }
          _throwIfClosed() {
            if (this.closed) throw new VC();
          }
          next(n) {
            $s(() => {
              if ((this._throwIfClosed(), !this.isStopped)) {
                this.currentObservers ||
                  (this.currentObservers = Array.from(this.observers));
                for (const r of this.currentObservers) r.next(n);
              }
            });
          }
          error(n) {
            $s(() => {
              if ((this._throwIfClosed(), !this.isStopped)) {
                (this.hasError = this.isStopped = !0), (this.thrownError = n);
                const { observers: r } = this;
                for (; r.length; ) r.shift().error(n);
              }
            });
          }
          complete() {
            $s(() => {
              if ((this._throwIfClosed(), !this.isStopped)) {
                this.isStopped = !0;
                const { observers: n } = this;
                for (; n.length; ) n.shift().complete();
              }
            });
          }
          unsubscribe() {
            (this.isStopped = this.closed = !0),
              (this.observers = this.currentObservers = null);
          }
          get observed() {
            var n;
            return (
              (null === (n = this.observers) || void 0 === n
                ? void 0
                : n.length) > 0
            );
          }
          _trySubscribe(n) {
            return this._throwIfClosed(), super._trySubscribe(n);
          }
          _subscribe(n) {
            return (
              this._throwIfClosed(),
              this._checkFinalizedStatuses(n),
              this._innerSubscribe(n)
            );
          }
          _innerSubscribe(n) {
            const { hasError: r, isStopped: i, observers: o } = this;
            return r || i
              ? Dp
              : ((this.currentObservers = null),
                o.push(n),
                new je(() => {
                  (this.currentObservers = null), Fr(o, n);
                }));
          }
          _checkFinalizedStatuses(n) {
            const { hasError: r, thrownError: i, isStopped: o } = this;
            r ? n.error(i) : o && n.complete();
          }
          asObservable() {
            const n = new pe();
            return (n.source = this), n;
          }
        }
        return (e.create = (t, n) => new Sp(t, n)), e;
      })();
      class Sp extends Te {
        constructor(t, n) {
          super(), (this.destination = t), (this.source = n);
        }
        next(t) {
          var n, r;
          null ===
            (r =
              null === (n = this.destination) || void 0 === n
                ? void 0
                : n.next) ||
            void 0 === r ||
            r.call(n, t);
        }
        error(t) {
          var n, r;
          null ===
            (r =
              null === (n = this.destination) || void 0 === n
                ? void 0
                : n.error) ||
            void 0 === r ||
            r.call(n, t);
        }
        complete() {
          var t, n;
          null ===
            (n =
              null === (t = this.destination) || void 0 === t
                ? void 0
                : t.complete) ||
            void 0 === n ||
            n.call(t);
        }
        _subscribe(t) {
          var n, r;
          return null !==
            (r =
              null === (n = this.source) || void 0 === n
                ? void 0
                : n.subscribe(t)) && void 0 !== r
            ? r
            : Dp;
        }
      }
      function xp(e) {
        return ne(e?.lift);
      }
      function De(e) {
        return (t) => {
          if (xp(t))
            return t.lift(function (n) {
              try {
                return e(n, this);
              } catch (r) {
                this.error(r);
              }
            });
          throw new TypeError("Unable to lift unknown Observable type");
        };
      }
      function be(e, t, n, r, i) {
        return new $C(e, t, n, r, i);
      }
      class $C extends Nl {
        constructor(t, n, r, i, o, s) {
          super(t),
            (this.onFinalize = o),
            (this.shouldUnsubscribe = s),
            (this._next = n
              ? function (a) {
                  try {
                    n(a);
                  } catch (c) {
                    t.error(c);
                  }
                }
              : super._next),
            (this._error = i
              ? function (a) {
                  try {
                    i(a);
                  } catch (c) {
                    t.error(c);
                  } finally {
                    this.unsubscribe();
                  }
                }
              : super._error),
            (this._complete = r
              ? function () {
                  try {
                    r();
                  } catch (a) {
                    t.error(a);
                  } finally {
                    this.unsubscribe();
                  }
                }
              : super._complete);
        }
        unsubscribe() {
          var t;
          if (!this.shouldUnsubscribe || this.shouldUnsubscribe()) {
            const { closed: n } = this;
            super.unsubscribe(),
              !n &&
                (null === (t = this.onFinalize) ||
                  void 0 === t ||
                  t.call(this));
          }
        }
      }
      function U(e, t) {
        return De((n, r) => {
          let i = 0;
          n.subscribe(
            be(r, (o) => {
              r.next(e.call(t, o, i++));
            }),
          );
        });
      }
      function Fn(e) {
        return this instanceof Fn ? ((this.v = e), this) : new Fn(e);
      }
      function Rp(e) {
        if (!Symbol.asyncIterator)
          throw new TypeError("Symbol.asyncIterator is not defined.");
        var n,
          t = e[Symbol.asyncIterator];
        return t
          ? t.call(e)
          : ((e = (function jl(e) {
              var t = "function" == typeof Symbol && Symbol.iterator,
                n = t && e[t],
                r = 0;
              if (n) return n.call(e);
              if (e && "number" == typeof e.length)
                return {
                  next: function () {
                    return (
                      e && r >= e.length && (e = void 0),
                      { value: e && e[r++], done: !e }
                    );
                  },
                };
              throw new TypeError(
                t
                  ? "Object is not iterable."
                  : "Symbol.iterator is not defined.",
              );
            })(e)),
            (n = {}),
            r("next"),
            r("throw"),
            r("return"),
            (n[Symbol.asyncIterator] = function () {
              return this;
            }),
            n);
        function r(o) {
          n[o] =
            e[o] &&
            function (s) {
              return new Promise(function (a, c) {
                !(function i(o, s, a, c) {
                  Promise.resolve(c).then(function (l) {
                    o({ value: l, done: a });
                  }, s);
                })(a, c, (s = e[o](s)).done, s.value);
              });
            };
        }
      }
      "function" == typeof SuppressedError && SuppressedError;
      const Op = (e) =>
        e && "number" == typeof e.length && "function" != typeof e;
      function Pp(e) {
        return ne(e?.then);
      }
      function kp(e) {
        return ne(e[Pl]);
      }
      function Fp(e) {
        return Symbol.asyncIterator && ne(e?.[Symbol.asyncIterator]);
      }
      function Lp(e) {
        return new TypeError(
          `You provided ${
            null !== e && "object" == typeof e ? "an invalid object" : `'${e}'`
          } where a stream was expected. You can provide an Observable, Promise, ReadableStream, Array, AsyncIterable, or Iterable.`,
        );
      }
      const jp = (function pI() {
        return "function" == typeof Symbol && Symbol.iterator
          ? Symbol.iterator
          : "@@iterator";
      })();
      function Bp(e) {
        return ne(e?.[jp]);
      }
      function Vp(e) {
        return (function Np(e, t, n) {
          if (!Symbol.asyncIterator)
            throw new TypeError("Symbol.asyncIterator is not defined.");
          var i,
            r = n.apply(e, t || []),
            o = [];
          return (
            (i = Object.create(
              ("function" == typeof AsyncIterator ? AsyncIterator : Object)
                .prototype,
            )),
            a("next"),
            a("throw"),
            a("return", function s(h) {
              return function (p) {
                return Promise.resolve(p).then(h, d);
              };
            }),
            (i[Symbol.asyncIterator] = function () {
              return this;
            }),
            i
          );
          function a(h, p) {
            r[h] &&
              ((i[h] = function (m) {
                return new Promise(function (g, y) {
                  o.push([h, m, g, y]) > 1 || c(h, m);
                });
              }),
              p && (i[h] = p(i[h])));
          }
          function c(h, p) {
            try {
              !(function l(h) {
                h.value instanceof Fn
                  ? Promise.resolve(h.value.v).then(u, d)
                  : f(o[0][2], h);
              })(r[h](p));
            } catch (m) {
              f(o[0][3], m);
            }
          }
          function u(h) {
            c("next", h);
          }
          function d(h) {
            c("throw", h);
          }
          function f(h, p) {
            h(p), o.shift(), o.length && c(o[0][0], o[0][1]);
          }
        })(this, arguments, function* () {
          const n = e.getReader();
          try {
            for (;;) {
              const { value: r, done: i } = yield Fn(n.read());
              if (i) return yield Fn(void 0);
              yield yield Fn(r);
            }
          } finally {
            n.releaseLock();
          }
        });
      }
      function $p(e) {
        return ne(e?.getReader);
      }
      function ct(e) {
        if (e instanceof pe) return e;
        if (null != e) {
          if (kp(e))
            return (function mI(e) {
              return new pe((t) => {
                const n = e[Pl]();
                if (ne(n.subscribe)) return n.subscribe(t);
                throw new TypeError(
                  "Provided object does not correctly implement Symbol.observable",
                );
              });
            })(e);
          if (Op(e))
            return (function gI(e) {
              return new pe((t) => {
                for (let n = 0; n < e.length && !t.closed; n++) t.next(e[n]);
                t.complete();
              });
            })(e);
          if (Pp(e))
            return (function bI(e) {
              return new pe((t) => {
                e.then(
                  (n) => {
                    t.closed || (t.next(n), t.complete());
                  },
                  (n) => t.error(n),
                ).then(null, Cp);
              });
            })(e);
          if (Fp(e)) return Up(e);
          if (Bp(e))
            return (function yI(e) {
              return new pe((t) => {
                for (const n of e) if ((t.next(n), t.closed)) return;
                t.complete();
              });
            })(e);
          if ($p(e))
            return (function vI(e) {
              return Up(Vp(e));
            })(e);
        }
        throw Lp(e);
      }
      function Up(e) {
        return new pe((t) => {
          (function _I(e, t) {
            var n, r, i, o;
            return (function Tp(e, t, n, r) {
              return new (n || (n = Promise))(function (o, s) {
                function a(u) {
                  try {
                    l(r.next(u));
                  } catch (d) {
                    s(d);
                  }
                }
                function c(u) {
                  try {
                    l(r.throw(u));
                  } catch (d) {
                    s(d);
                  }
                }
                function l(u) {
                  u.done
                    ? o(u.value)
                    : (function i(o) {
                        return o instanceof n
                          ? o
                          : new n(function (s) {
                              s(o);
                            });
                      })(u.value).then(a, c);
                }
                l((r = r.apply(e, t || [])).next());
              });
            })(this, void 0, void 0, function* () {
              try {
                for (n = Rp(e); !(r = yield n.next()).done; )
                  if ((t.next(r.value), t.closed)) return;
              } catch (s) {
                i = { error: s };
              } finally {
                try {
                  r && !r.done && (o = n.return) && (yield o.call(n));
                } finally {
                  if (i) throw i.error;
                }
              }
              t.complete();
            });
          })(e, t).catch((n) => t.error(n));
        });
      }
      function pn(e, t, n, r = 0, i = !1) {
        const o = t.schedule(function () {
          n(), i ? e.add(this.schedule(null, r)) : this.unsubscribe();
        }, r);
        if ((e.add(o), !i)) return o;
      }
      function Ae(e, t, n = 1 / 0) {
        return ne(t)
          ? Ae((r, i) => U((o, s) => t(r, o, i, s))(ct(e(r, i))), n)
          : ("number" == typeof t && (n = t),
            De((r, i) =>
              (function DI(e, t, n, r, i, o, s, a) {
                const c = [];
                let l = 0,
                  u = 0,
                  d = !1;
                const f = () => {
                    d && !c.length && !l && t.complete();
                  },
                  h = (m) => (l < r ? p(m) : c.push(m)),
                  p = (m) => {
                    o && t.next(m), l++;
                    let g = !1;
                    ct(n(m, u++)).subscribe(
                      be(
                        t,
                        (y) => {
                          i?.(y), o ? h(y) : t.next(y);
                        },
                        () => {
                          g = !0;
                        },
                        void 0,
                        () => {
                          if (g)
                            try {
                              for (l--; c.length && l < r; ) {
                                const y = c.shift();
                                s ? pn(t, s, () => p(y)) : p(y);
                              }
                              f();
                            } catch (y) {
                              t.error(y);
                            }
                        },
                      ),
                    );
                  };
                return (
                  e.subscribe(
                    be(t, h, () => {
                      (d = !0), f();
                    }),
                  ),
                  () => {
                    a?.();
                  }
                );
              })(r, i, e, n),
            ));
      }
      function Lr(e = 1 / 0) {
        return Ae(kn, e);
      }
      const Zt = new pe((e) => e.complete());
      function Vl(e) {
        return e[e.length - 1];
      }
      function Hp(e) {
        return ne(Vl(e)) ? e.pop() : void 0;
      }
      function no(e) {
        return (function EI(e) {
          return e && ne(e.schedule);
        })(Vl(e))
          ? e.pop()
          : void 0;
      }
      function zp(e, t = 0) {
        return De((n, r) => {
          n.subscribe(
            be(
              r,
              (i) => pn(r, e, () => r.next(i), t),
              () => pn(r, e, () => r.complete(), t),
              (i) => pn(r, e, () => r.error(i), t),
            ),
          );
        });
      }
      function qp(e, t = 0) {
        return De((n, r) => {
          r.add(e.schedule(() => n.subscribe(r), t));
        });
      }
      function Gp(e, t) {
        if (!e) throw new Error("Iterable cannot be null");
        return new pe((n) => {
          pn(n, t, () => {
            const r = e[Symbol.asyncIterator]();
            pn(
              n,
              t,
              () => {
                r.next().then((i) => {
                  i.done ? n.complete() : n.next(i.value);
                });
              },
              0,
              !0,
            );
          });
        });
      }
      function Se(e, t) {
        return t
          ? (function AI(e, t) {
              if (null != e) {
                if (kp(e))
                  return (function II(e, t) {
                    return ct(e).pipe(qp(t), zp(t));
                  })(e, t);
                if (Op(e))
                  return (function SI(e, t) {
                    return new pe((n) => {
                      let r = 0;
                      return t.schedule(function () {
                        r === e.length
                          ? n.complete()
                          : (n.next(e[r++]), n.closed || this.schedule());
                      });
                    });
                  })(e, t);
                if (Pp(e))
                  return (function MI(e, t) {
                    return ct(e).pipe(qp(t), zp(t));
                  })(e, t);
                if (Fp(e)) return Gp(e, t);
                if (Bp(e))
                  return (function xI(e, t) {
                    return new pe((n) => {
                      let r;
                      return (
                        pn(n, t, () => {
                          (r = e[jp]()),
                            pn(
                              n,
                              t,
                              () => {
                                let i, o;
                                try {
                                  ({ value: i, done: o } = r.next());
                                } catch (s) {
                                  return void n.error(s);
                                }
                                o ? n.complete() : n.next(i);
                              },
                              0,
                              !0,
                            );
                        }),
                        () => ne(r?.return) && r.return()
                      );
                    });
                  })(e, t);
                if ($p(e))
                  return (function TI(e, t) {
                    return Gp(Vp(e), t);
                  })(e, t);
              }
              throw Lp(e);
            })(e, t)
          : ct(e);
      }
      class lt extends Te {
        constructor(t) {
          super(), (this._value = t);
        }
        get value() {
          return this.getValue();
        }
        _subscribe(t) {
          const n = super._subscribe(t);
          return !n.closed && t.next(this._value), n;
        }
        getValue() {
          const { hasError: t, thrownError: n, _value: r } = this;
          if (t) throw n;
          return this._throwIfClosed(), r;
        }
        next(t) {
          super.next((this._value = t));
        }
      }
      function A(...e) {
        return Se(e, no(e));
      }
      function $l(e = {}) {
        const {
          connector: t = () => new Te(),
          resetOnError: n = !0,
          resetOnComplete: r = !0,
          resetOnRefCountZero: i = !0,
        } = e;
        return (o) => {
          let s,
            a,
            c,
            l = 0,
            u = !1,
            d = !1;
          const f = () => {
              a?.unsubscribe(), (a = void 0);
            },
            h = () => {
              f(), (s = c = void 0), (u = d = !1);
            },
            p = () => {
              const m = s;
              h(), m?.unsubscribe();
            };
          return De((m, g) => {
            l++, !d && !u && f();
            const y = (c = c ?? t());
            g.add(() => {
              l--, 0 === l && !d && !u && (a = Ul(p, i));
            }),
              y.subscribe(g),
              !s &&
                l > 0 &&
                ((s = new to({
                  next: (b) => y.next(b),
                  error: (b) => {
                    (d = !0), f(), (a = Ul(h, n, b)), y.error(b);
                  },
                  complete: () => {
                    (u = !0), f(), (a = Ul(h, r)), y.complete();
                  },
                })),
                ct(m).subscribe(s));
          })(o);
        };
      }
      function Ul(e, t, ...n) {
        if (!0 === t) return void e();
        if (!1 === t) return;
        const r = new to({
          next: () => {
            r.unsubscribe(), e();
          },
        });
        return ct(t(...n)).subscribe(r);
      }
      function Ft(e, t) {
        return De((n, r) => {
          let i = null,
            o = 0,
            s = !1;
          const a = () => s && !i && r.complete();
          n.subscribe(
            be(
              r,
              (c) => {
                i?.unsubscribe();
                let l = 0;
                const u = o++;
                ct(e(c, u)).subscribe(
                  (i = be(
                    r,
                    (d) => r.next(t ? t(c, d, u, l++) : d),
                    () => {
                      (i = null), a();
                    },
                  )),
                );
              },
              () => {
                (s = !0), a();
              },
            ),
          );
        });
      }
      function Wp(e, t = kn) {
        return (
          (e = e ?? RI),
          De((n, r) => {
            let i,
              o = !0;
            n.subscribe(
              be(r, (s) => {
                const a = t(s);
                (o || !e(i, a)) && ((o = !1), (i = a), r.next(s));
              }),
            );
          })
        );
      }
      function RI(e, t) {
        return e === t;
      }
      function J(e) {
        for (let t in e) if (e[t] === J) return t;
        throw Error("Could not find renamed property on target object.");
      }
      function Hs(e, t) {
        for (const n in t)
          t.hasOwnProperty(n) && !e.hasOwnProperty(n) && (e[n] = t[n]);
      }
      function Ce(e) {
        if ("string" == typeof e) return e;
        if (Array.isArray(e)) return "[" + e.map(Ce).join(", ") + "]";
        if (null == e) return "" + e;
        if (e.overriddenName) return `${e.overriddenName}`;
        if (e.name) return `${e.name}`;
        const t = e.toString();
        if (null == t) return "" + t;
        const n = t.indexOf("\n");
        return -1 === n ? t : t.substring(0, n);
      }
      function Hl(e, t) {
        return null == e || "" === e
          ? null === t
            ? ""
            : t
          : null == t || "" === t
          ? e
          : e + " " + t;
      }
      const OI = J({ __forward_ref__: J });
      function zl(e) {
        return (
          (e.__forward_ref__ = zl),
          (e.toString = function () {
            return Ce(this());
          }),
          e
        );
      }
      function k(e) {
        return ql(e) ? e() : e;
      }
      function ql(e) {
        return (
          "function" == typeof e &&
          e.hasOwnProperty(OI) &&
          e.__forward_ref__ === zl
        );
      }
      function Gl(e) {
        return e && !!e.ɵproviders;
      }
      const Kp = "https://g.co/ng/security#xss";
      class v extends Error {
        constructor(t, n) {
          super(
            (function zs(e, t) {
              return `NG0${Math.abs(e)}${t ? ": " + t : ""}`;
            })(t, n),
          ),
            (this.code = t);
        }
      }
      function L(e) {
        return "string" == typeof e ? e : null == e ? "" : String(e);
      }
      function Wl(e, t) {
        throw new v(-201, !1);
      }
      function Ct(e, t) {
        null == e &&
          (function O(e, t, n, r) {
            throw new Error(
              `ASSERTION ERROR: ${e}` +
                (null == r ? "" : ` [Expected=> ${n} ${r} ${t} <=Actual]`),
            );
          })(t, e, null, "!=");
      }
      function S(e) {
        return {
          token: e.token,
          providedIn: e.providedIn || null,
          factory: e.factory,
          value: void 0,
        };
      }
      function Ne(e) {
        return { providers: e.providers || [], imports: e.imports || [] };
      }
      function qs(e) {
        return Zp(e, Ws) || Zp(e, Qp);
      }
      function Zp(e, t) {
        return e.hasOwnProperty(t) ? e[t] : null;
      }
      function Gs(e) {
        return e && (e.hasOwnProperty(Kl) || e.hasOwnProperty($I))
          ? e[Kl]
          : null;
      }
      const Ws = J({ ɵprov: J }),
        Kl = J({ ɵinj: J }),
        Qp = J({ ngInjectableDef: J }),
        $I = J({ ngInjectorDef: J });
      var H = (function (e) {
        return (
          (e[(e.Default = 0)] = "Default"),
          (e[(e.Host = 1)] = "Host"),
          (e[(e.Self = 2)] = "Self"),
          (e[(e.SkipSelf = 4)] = "SkipSelf"),
          (e[(e.Optional = 8)] = "Optional"),
          e
        );
      })(H || {});
      let Zl;
      function tt(e) {
        const t = Zl;
        return (Zl = e), t;
      }
      function Xp(e, t, n) {
        const r = qs(e);
        return r && "root" == r.providedIn
          ? void 0 === r.value
            ? (r.value = r.factory())
            : r.value
          : n & H.Optional
          ? null
          : void 0 !== t
          ? t
          : void Wl(Ce(e));
      }
      const oe = globalThis;
      class E {
        constructor(t, n) {
          (this._desc = t),
            (this.ngMetadataName = "InjectionToken"),
            (this.ɵprov = void 0),
            "number" == typeof n
              ? (this.__NG_ELEMENT_ID__ = n)
              : void 0 !== n &&
                (this.ɵprov = S({
                  token: this,
                  providedIn: n.providedIn || "root",
                  factory: n.factory,
                }));
        }
        get multi() {
          return this;
        }
        toString() {
          return `InjectionToken ${this._desc}`;
        }
      }
      const ro = {},
        eu = "__NG_DI_FLAG__",
        Ks = "ngTempTokenPath",
        zI = /\n/gm,
        em = "__source";
      let jr;
      function Ln(e) {
        const t = jr;
        return (jr = e), t;
      }
      function WI(e, t = H.Default) {
        if (void 0 === jr) throw new v(-203, !1);
        return null === jr
          ? Xp(e, void 0, t)
          : jr.get(e, t & H.Optional ? null : void 0, t);
      }
      function D(e, t = H.Default) {
        return (
          (function Yp() {
            return Zl;
          })() || WI
        )(k(e), t);
      }
      function C(e, t = H.Default) {
        return D(e, Zs(t));
      }
      function Zs(e) {
        return typeof e > "u" || "number" == typeof e
          ? e
          : 0 |
              (e.optional && 8) |
              (e.host && 1) |
              (e.self && 2) |
              (e.skipSelf && 4);
      }
      function tu(e) {
        const t = [];
        for (let n = 0; n < e.length; n++) {
          const r = k(e[n]);
          if (Array.isArray(r)) {
            if (0 === r.length) throw new v(900, !1);
            let i,
              o = H.Default;
            for (let s = 0; s < r.length; s++) {
              const a = r[s],
                c = KI(a);
              "number" == typeof c
                ? -1 === c
                  ? (i = a.token)
                  : (o |= c)
                : (i = a);
            }
            t.push(D(i, o));
          } else t.push(D(r));
        }
        return t;
      }
      function io(e, t) {
        return (e[eu] = t), (e.prototype[eu] = t), e;
      }
      function KI(e) {
        return e[eu];
      }
      function mn(e) {
        return { toString: e }.toString();
      }
      var Qs = (function (e) {
          return (
            (e[(e.OnPush = 0)] = "OnPush"), (e[(e.Default = 1)] = "Default"), e
          );
        })(Qs || {}),
        It = (function (e) {
          return (
            (e[(e.Emulated = 0)] = "Emulated"),
            (e[(e.None = 2)] = "None"),
            (e[(e.ShadowDom = 3)] = "ShadowDom"),
            e
          );
        })(It || {});
      const Qt = {},
        Z = [],
        Ys = J({ ɵcmp: J }),
        nu = J({ ɵdir: J }),
        ru = J({ ɵpipe: J }),
        nm = J({ ɵmod: J }),
        gn = J({ ɵfac: J }),
        oo = J({ __NG_ELEMENT_ID__: J }),
        rm = J({ __NG_ENV_ID__: J });
      function im(e, t, n) {
        let r = e.length;
        for (;;) {
          const i = e.indexOf(t, n);
          if (-1 === i) return i;
          if (0 === i || e.charCodeAt(i - 1) <= 32) {
            const o = t.length;
            if (i + o === r || e.charCodeAt(i + o) <= 32) return i;
          }
          n = i + 1;
        }
      }
      function iu(e, t, n) {
        let r = 0;
        for (; r < n.length; ) {
          const i = n[r];
          if ("number" == typeof i) {
            if (0 !== i) break;
            r++;
            const o = n[r++],
              s = n[r++],
              a = n[r++];
            e.setAttribute(t, s, a, o);
          } else {
            const o = i,
              s = n[++r];
            sm(o) ? e.setProperty(t, o, s) : e.setAttribute(t, o, s), r++;
          }
        }
        return r;
      }
      function om(e) {
        return 3 === e || 4 === e || 6 === e;
      }
      function sm(e) {
        return 64 === e.charCodeAt(0);
      }
      function so(e, t) {
        if (null !== t && 0 !== t.length)
          if (null === e || 0 === e.length) e = t.slice();
          else {
            let n = -1;
            for (let r = 0; r < t.length; r++) {
              const i = t[r];
              "number" == typeof i
                ? (n = i)
                : 0 === n ||
                  am(e, n, i, null, -1 === n || 2 === n ? t[++r] : null);
            }
          }
        return e;
      }
      function am(e, t, n, r, i) {
        let o = 0,
          s = e.length;
        if (-1 === t) s = -1;
        else
          for (; o < e.length; ) {
            const a = e[o++];
            if ("number" == typeof a) {
              if (a === t) {
                s = -1;
                break;
              }
              if (a > t) {
                s = o - 1;
                break;
              }
            }
          }
        for (; o < e.length; ) {
          const a = e[o];
          if ("number" == typeof a) break;
          if (a === n) {
            if (null === r) return void (null !== i && (e[o + 1] = i));
            if (r === e[o + 1]) return void (e[o + 2] = i);
          }
          o++, null !== r && o++, null !== i && o++;
        }
        -1 !== s && (e.splice(s, 0, t), (o = s + 1)),
          e.splice(o++, 0, n),
          null !== r && e.splice(o++, 0, r),
          null !== i && e.splice(o++, 0, i);
      }
      const cm = "ng-template";
      function YI(e, t, n) {
        let r = 0,
          i = !0;
        for (; r < e.length; ) {
          let o = e[r++];
          if ("string" == typeof o && i) {
            const s = e[r++];
            if (n && "class" === o && -1 !== im(s.toLowerCase(), t, 0))
              return !0;
          } else {
            if (1 === o) {
              for (; r < e.length && "string" == typeof (o = e[r++]); )
                if (o.toLowerCase() === t) return !0;
              return !1;
            }
            "number" == typeof o && (i = !1);
          }
        }
        return !1;
      }
      function lm(e) {
        return 4 === e.type && e.value !== cm;
      }
      function XI(e, t, n) {
        return t === (4 !== e.type || n ? e.value : cm);
      }
      function JI(e, t, n) {
        let r = 4;
        const i = e.attrs || [],
          o = (function nM(e) {
            for (let t = 0; t < e.length; t++) if (om(e[t])) return t;
            return e.length;
          })(i);
        let s = !1;
        for (let a = 0; a < t.length; a++) {
          const c = t[a];
          if ("number" != typeof c) {
            if (!s)
              if (4 & r) {
                if (
                  ((r = 2 | (1 & r)),
                  ("" !== c && !XI(e, c, n)) || ("" === c && 1 === t.length))
                ) {
                  if (Lt(r)) return !1;
                  s = !0;
                }
              } else {
                const l = 8 & r ? c : t[++a];
                if (8 & r && null !== e.attrs) {
                  if (!YI(e.attrs, l, n)) {
                    if (Lt(r)) return !1;
                    s = !0;
                  }
                  continue;
                }
                const d = eM(8 & r ? "class" : c, i, lm(e), n);
                if (-1 === d) {
                  if (Lt(r)) return !1;
                  s = !0;
                  continue;
                }
                if ("" !== l) {
                  let f;
                  f = d > o ? "" : i[d + 1].toLowerCase();
                  const h = 8 & r ? f : null;
                  if ((h && -1 !== im(h, l, 0)) || (2 & r && l !== f)) {
                    if (Lt(r)) return !1;
                    s = !0;
                  }
                }
              }
          } else {
            if (!s && !Lt(r) && !Lt(c)) return !1;
            if (s && Lt(c)) continue;
            (s = !1), (r = c | (1 & r));
          }
        }
        return Lt(r) || s;
      }
      function Lt(e) {
        return 0 == (1 & e);
      }
      function eM(e, t, n, r) {
        if (null === t) return -1;
        let i = 0;
        if (r || !n) {
          let o = !1;
          for (; i < t.length; ) {
            const s = t[i];
            if (s === e) return i;
            if (3 === s || 6 === s) o = !0;
            else {
              if (1 === s || 2 === s) {
                let a = t[++i];
                for (; "string" == typeof a; ) a = t[++i];
                continue;
              }
              if (4 === s) break;
              if (0 === s) {
                i += 4;
                continue;
              }
            }
            i += o ? 1 : 2;
          }
          return -1;
        }
        return (function rM(e, t) {
          let n = e.indexOf(4);
          if (n > -1)
            for (n++; n < e.length; ) {
              const r = e[n];
              if ("number" == typeof r) return -1;
              if (r === t) return n;
              n++;
            }
          return -1;
        })(t, e);
      }
      function um(e, t, n = !1) {
        for (let r = 0; r < t.length; r++) if (JI(e, t[r], n)) return !0;
        return !1;
      }
      function iM(e, t) {
        e: for (let n = 0; n < t.length; n++) {
          const r = t[n];
          if (e.length === r.length) {
            for (let i = 0; i < e.length; i++) if (e[i] !== r[i]) continue e;
            return !0;
          }
        }
        return !1;
      }
      function dm(e, t) {
        return e ? ":not(" + t.trim() + ")" : t;
      }
      function oM(e) {
        let t = e[0],
          n = 1,
          r = 2,
          i = "",
          o = !1;
        for (; n < e.length; ) {
          let s = e[n];
          if ("string" == typeof s)
            if (2 & r) {
              const a = e[++n];
              i += "[" + s + (a.length > 0 ? '="' + a + '"' : "") + "]";
            } else 8 & r ? (i += "." + s) : 4 & r && (i += " " + s);
          else
            "" !== i && !Lt(s) && ((t += dm(o, i)), (i = "")),
              (r = s),
              (o = o || !Lt(r));
          n++;
        }
        return "" !== i && (t += dm(o, i)), t;
      }
      function bn(e) {
        return mn(() => {
          const t = hm(e),
            n = {
              ...t,
              decls: e.decls,
              vars: e.vars,
              template: e.template,
              consts: e.consts || null,
              ngContentSelectors: e.ngContentSelectors,
              onPush: e.changeDetection === Qs.OnPush,
              directiveDefs: null,
              pipeDefs: null,
              dependencies: (t.standalone && e.dependencies) || null,
              getStandaloneInjector: null,
              signals: e.signals ?? !1,
              data: e.data || {},
              encapsulation: e.encapsulation || It.Emulated,
              styles: e.styles || Z,
              _: null,
              schemas: e.schemas || null,
              tView: null,
              id: "",
            };
          pm(n);
          const r = e.dependencies;
          return (
            (n.directiveDefs = Xs(r, !1)),
            (n.pipeDefs = Xs(r, !0)),
            (n.id = (function hM(e) {
              let t = 0;
              const n = [
                e.selectors,
                e.ngContentSelectors,
                e.hostVars,
                e.hostAttrs,
                e.consts,
                e.vars,
                e.decls,
                e.encapsulation,
                e.standalone,
                e.signals,
                e.exportAs,
                JSON.stringify(e.inputs),
                JSON.stringify(e.outputs),
                Object.getOwnPropertyNames(e.type.prototype),
                !!e.contentQueries,
                !!e.viewQuery,
              ].join("|");
              for (const i of n) t = (Math.imul(31, t) + i.charCodeAt(0)) << 0;
              return (t += 2147483648), "c" + t;
            })(n)),
            n
          );
        });
      }
      function lM(e) {
        return q(e) || Re(e);
      }
      function uM(e) {
        return null !== e;
      }
      function Be(e) {
        return mn(() => ({
          type: e.type,
          bootstrap: e.bootstrap || Z,
          declarations: e.declarations || Z,
          imports: e.imports || Z,
          exports: e.exports || Z,
          transitiveCompileScopes: null,
          schemas: e.schemas || null,
          id: e.id || null,
        }));
      }
      function fm(e, t) {
        if (null == e) return Qt;
        const n = {};
        for (const r in e)
          if (e.hasOwnProperty(r)) {
            let i = e[r],
              o = i;
            Array.isArray(i) && ((o = i[1]), (i = i[0])),
              (n[i] = r),
              t && (t[i] = o);
          }
        return n;
      }
      function re(e) {
        return mn(() => {
          const t = hm(e);
          return pm(t), t;
        });
      }
      function q(e) {
        return e[Ys] || null;
      }
      function Re(e) {
        return e[nu] || null;
      }
      function Ge(e) {
        return e[ru] || null;
      }
      function dt(e, t) {
        const n = e[nm] || null;
        if (!n && !0 === t)
          throw new Error(`Type ${Ce(e)} does not have '\u0275mod' property.`);
        return n;
      }
      function hm(e) {
        const t = {};
        return {
          type: e.type,
          providersResolver: null,
          factory: null,
          hostBindings: e.hostBindings || null,
          hostVars: e.hostVars || 0,
          hostAttrs: e.hostAttrs || null,
          contentQueries: e.contentQueries || null,
          declaredInputs: t,
          inputTransforms: null,
          inputConfig: e.inputs || Qt,
          exportAs: e.exportAs || null,
          standalone: !0 === e.standalone,
          signals: !0 === e.signals,
          selectors: e.selectors || Z,
          viewQuery: e.viewQuery || null,
          features: e.features || null,
          setInput: null,
          findHostDirectiveDefs: null,
          hostDirectives: null,
          inputs: fm(e.inputs, t),
          outputs: fm(e.outputs),
        };
      }
      function pm(e) {
        e.features?.forEach((t) => t(e));
      }
      function Xs(e, t) {
        if (!e) return null;
        const n = t ? Ge : lM;
        return () =>
          ("function" == typeof e ? e() : e).map((r) => n(r)).filter(uM);
      }
      const me = 0,
        I = 1,
        V = 2,
        de = 3,
        jt = 4,
        ao = 5,
        Ve = 6,
        Vr = 7,
        ye = 8,
        jn = 9,
        $r = 10,
        j = 11,
        co = 12,
        mm = 13,
        Ur = 14,
        ve = 15,
        lo = 16,
        Hr = 17,
        Yt = 18,
        uo = 19,
        gm = 20,
        Bn = 21,
        yn = 22,
        fo = 23,
        ho = 24,
        z = 25,
        ou = 1,
        bm = 2,
        Xt = 7,
        zr = 9,
        Oe = 11;
      function rt(e) {
        return Array.isArray(e) && "object" == typeof e[ou];
      }
      function We(e) {
        return Array.isArray(e) && !0 === e[ou];
      }
      function su(e) {
        return 0 != (4 & e.flags);
      }
      function sr(e) {
        return e.componentOffset > -1;
      }
      function ea(e) {
        return 1 == (1 & e.flags);
      }
      function Bt(e) {
        return !!e.template;
      }
      function au(e) {
        return 0 != (512 & e[V]);
      }
      function ar(e, t) {
        return e.hasOwnProperty(gn) ? e[gn] : null;
      }
      let Pe = null,
        ta = !1;
      function Mt(e) {
        const t = Pe;
        return (Pe = e), t;
      }
      const _m = {
        version: 0,
        dirty: !1,
        producerNode: void 0,
        producerLastReadVersion: void 0,
        producerIndexOfThis: void 0,
        nextProducerIndex: 0,
        liveConsumerNode: void 0,
        liveConsumerIndexOfThis: void 0,
        consumerAllowSignalWrites: !1,
        consumerIsAlwaysLive: !1,
        producerMustRecompute: () => !1,
        producerRecomputeValue: () => {},
        consumerMarkedDirty: () => {},
      };
      function wm(e) {
        if (!mo(e) || e.dirty) {
          if (!e.producerMustRecompute(e) && !Im(e)) return void (e.dirty = !1);
          e.producerRecomputeValue(e), (e.dirty = !1);
        }
      }
      function Cm(e) {
        (e.dirty = !0),
          (function Em(e) {
            if (void 0 === e.liveConsumerNode) return;
            const t = ta;
            ta = !0;
            try {
              for (const n of e.liveConsumerNode) n.dirty || Cm(n);
            } finally {
              ta = t;
            }
          })(e),
          e.consumerMarkedDirty?.(e);
      }
      function lu(e) {
        return e && (e.nextProducerIndex = 0), Mt(e);
      }
      function uu(e, t) {
        if (
          (Mt(t),
          e &&
            void 0 !== e.producerNode &&
            void 0 !== e.producerIndexOfThis &&
            void 0 !== e.producerLastReadVersion)
        ) {
          if (mo(e))
            for (let n = e.nextProducerIndex; n < e.producerNode.length; n++)
              na(e.producerNode[n], e.producerIndexOfThis[n]);
          for (; e.producerNode.length > e.nextProducerIndex; )
            e.producerNode.pop(),
              e.producerLastReadVersion.pop(),
              e.producerIndexOfThis.pop();
        }
      }
      function Im(e) {
        qr(e);
        for (let t = 0; t < e.producerNode.length; t++) {
          const n = e.producerNode[t],
            r = e.producerLastReadVersion[t];
          if (r !== n.version || (wm(n), r !== n.version)) return !0;
        }
        return !1;
      }
      function Mm(e) {
        if ((qr(e), mo(e)))
          for (let t = 0; t < e.producerNode.length; t++)
            na(e.producerNode[t], e.producerIndexOfThis[t]);
        (e.producerNode.length =
          e.producerLastReadVersion.length =
          e.producerIndexOfThis.length =
            0),
          e.liveConsumerNode &&
            (e.liveConsumerNode.length = e.liveConsumerIndexOfThis.length = 0);
      }
      function na(e, t) {
        if (
          ((function xm(e) {
            (e.liveConsumerNode ??= []), (e.liveConsumerIndexOfThis ??= []);
          })(e),
          qr(e),
          1 === e.liveConsumerNode.length)
        )
          for (let r = 0; r < e.producerNode.length; r++)
            na(e.producerNode[r], e.producerIndexOfThis[r]);
        const n = e.liveConsumerNode.length - 1;
        if (
          ((e.liveConsumerNode[t] = e.liveConsumerNode[n]),
          (e.liveConsumerIndexOfThis[t] = e.liveConsumerIndexOfThis[n]),
          e.liveConsumerNode.length--,
          e.liveConsumerIndexOfThis.length--,
          t < e.liveConsumerNode.length)
        ) {
          const r = e.liveConsumerIndexOfThis[t],
            i = e.liveConsumerNode[t];
          qr(i), (i.producerIndexOfThis[r] = t);
        }
      }
      function mo(e) {
        return e.consumerIsAlwaysLive || (e?.liveConsumerNode?.length ?? 0) > 0;
      }
      function qr(e) {
        (e.producerNode ??= []),
          (e.producerIndexOfThis ??= []),
          (e.producerLastReadVersion ??= []);
      }
      let Tm = null;
      const Om = () => {},
        MM = (() => ({
          ..._m,
          consumerIsAlwaysLive: !0,
          consumerAllowSignalWrites: !1,
          consumerMarkedDirty: (e) => {
            e.schedule(e.ref);
          },
          hasRun: !1,
          cleanupFn: Om,
        }))();
      class SM {
        constructor(t, n, r) {
          (this.previousValue = t),
            (this.currentValue = n),
            (this.firstChange = r);
        }
        isFirstChange() {
          return this.firstChange;
        }
      }
      function cr() {
        return Pm;
      }
      function Pm(e) {
        return e.type.prototype.ngOnChanges && (e.setInput = TM), xM;
      }
      function xM() {
        const e = Fm(this),
          t = e?.current;
        if (t) {
          const n = e.previous;
          if (n === Qt) e.previous = t;
          else for (let r in t) n[r] = t[r];
          (e.current = null), this.ngOnChanges(t);
        }
      }
      function TM(e, t, n, r) {
        const i = this.declaredInputs[n],
          o =
            Fm(e) ||
            (function AM(e, t) {
              return (e[km] = t);
            })(e, { previous: Qt, current: null }),
          s = o.current || (o.current = {}),
          a = o.previous,
          c = a[i];
        (s[i] = new SM(c && c.currentValue, t, a === Qt)), (e[r] = t);
      }
      cr.ngInherit = !0;
      const km = "__ngSimpleChanges__";
      function Fm(e) {
        return e[km] || null;
      }
      const Jt = function (e, t, n) {};
      function se(e) {
        for (; Array.isArray(e); ) e = e[me];
        return e;
      }
      function ra(e, t) {
        return se(t[e]);
      }
      function it(e, t) {
        return se(t[e.index]);
      }
      function Bm(e, t) {
        return e.data[t];
      }
      function ft(e, t) {
        const n = t[e];
        return rt(n) ? n : n[me];
      }
      function $n(e, t) {
        return null == t ? null : e[t];
      }
      function Vm(e) {
        e[Hr] = 0;
      }
      function FM(e) {
        1024 & e[V] || ((e[V] |= 1024), Um(e, 1));
      }
      function $m(e) {
        1024 & e[V] && ((e[V] &= -1025), Um(e, -1));
      }
      function Um(e, t) {
        let n = e[de];
        if (null === n) return;
        n[ao] += t;
        let r = n;
        for (
          n = n[de];
          null !== n && ((1 === t && 1 === r[ao]) || (-1 === t && 0 === r[ao]));

        )
          (n[ao] += t), (r = n), (n = n[de]);
      }
      const P = {
        lFrame: Jm(null),
        bindingsEnabled: !0,
        skipHydrationRootTNode: null,
      };
      function qm() {
        return P.bindingsEnabled;
      }
      function Wr() {
        return null !== P.skipHydrationRootTNode;
      }
      function _() {
        return P.lFrame.lView;
      }
      function G() {
        return P.lFrame.tView;
      }
      function ke() {
        let e = Gm();
        for (; null !== e && 64 === e.type; ) e = e.parent;
        return e;
      }
      function Gm() {
        return P.lFrame.currentTNode;
      }
      function en(e, t) {
        const n = P.lFrame;
        (n.currentTNode = e), (n.isParent = t);
      }
      function mu() {
        return P.lFrame.isParent;
      }
      function gu() {
        P.lFrame.isParent = !1;
      }
      function Kr() {
        return P.lFrame.bindingIndex++;
      }
      function QM(e, t) {
        const n = P.lFrame;
        (n.bindingIndex = n.bindingRootIndex = e), bu(t);
      }
      function bu(e) {
        P.lFrame.currentDirectiveIndex = e;
      }
      function vu(e) {
        P.lFrame.currentQueryIndex = e;
      }
      function XM(e) {
        const t = e[I];
        return 2 === t.type ? t.declTNode : 1 === t.type ? e[Ve] : null;
      }
      function Ym(e, t, n) {
        if (n & H.SkipSelf) {
          let i = t,
            o = e;
          for (
            ;
            !((i = i.parent),
            null !== i ||
              n & H.Host ||
              ((i = XM(o)), null === i || ((o = o[Ur]), 10 & i.type)));

          );
          if (null === i) return !1;
          (t = i), (e = o);
        }
        const r = (P.lFrame = Xm());
        return (r.currentTNode = t), (r.lView = e), !0;
      }
      function _u(e) {
        const t = Xm(),
          n = e[I];
        (P.lFrame = t),
          (t.currentTNode = n.firstChild),
          (t.lView = e),
          (t.tView = n),
          (t.contextLView = e),
          (t.bindingIndex = n.bindingStartIndex),
          (t.inI18n = !1);
      }
      function Xm() {
        const e = P.lFrame,
          t = null === e ? null : e.child;
        return null === t ? Jm(e) : t;
      }
      function Jm(e) {
        const t = {
          currentTNode: null,
          isParent: !0,
          lView: null,
          tView: null,
          selectedIndex: -1,
          contextLView: null,
          elementDepthCount: 0,
          currentNamespace: null,
          currentDirectiveIndex: -1,
          bindingRootIndex: -1,
          bindingIndex: -1,
          currentQueryIndex: 0,
          parent: e,
          child: null,
          inI18n: !1,
        };
        return null !== e && (e.child = t), t;
      }
      function eg() {
        const e = P.lFrame;
        return (
          (P.lFrame = e.parent), (e.currentTNode = null), (e.lView = null), e
        );
      }
      const tg = eg;
      function Du() {
        const e = eg();
        (e.isParent = !0),
          (e.tView = null),
          (e.selectedIndex = -1),
          (e.contextLView = null),
          (e.elementDepthCount = 0),
          (e.currentDirectiveIndex = -1),
          (e.currentNamespace = null),
          (e.bindingRootIndex = -1),
          (e.bindingIndex = -1),
          (e.currentQueryIndex = 0);
      }
      function Ze() {
        return P.lFrame.selectedIndex;
      }
      function lr(e) {
        P.lFrame.selectedIndex = e;
      }
      function fe() {
        const e = P.lFrame;
        return Bm(e.tView, e.selectedIndex);
      }
      let rg = !0;
      function ia() {
        return rg;
      }
      function Un(e) {
        rg = e;
      }
      function oa(e, t) {
        for (let n = t.directiveStart, r = t.directiveEnd; n < r; n++) {
          const o = e.data[n].type.prototype,
            {
              ngAfterContentInit: s,
              ngAfterContentChecked: a,
              ngAfterViewInit: c,
              ngAfterViewChecked: l,
              ngOnDestroy: u,
            } = o;
          s && (e.contentHooks ??= []).push(-n, s),
            a &&
              ((e.contentHooks ??= []).push(n, a),
              (e.contentCheckHooks ??= []).push(n, a)),
            c && (e.viewHooks ??= []).push(-n, c),
            l &&
              ((e.viewHooks ??= []).push(n, l),
              (e.viewCheckHooks ??= []).push(n, l)),
            null != u && (e.destroyHooks ??= []).push(n, u);
        }
      }
      function sa(e, t, n) {
        ig(e, t, 3, n);
      }
      function aa(e, t, n, r) {
        (3 & e[V]) === n && ig(e, t, n, r);
      }
      function wu(e, t) {
        let n = e[V];
        (3 & n) === t && ((n &= 8191), (n += 1), (e[V] = n));
      }
      function ig(e, t, n, r) {
        const o = r ?? -1,
          s = t.length - 1;
        let a = 0;
        for (let c = void 0 !== r ? 65535 & e[Hr] : 0; c < s; c++)
          if ("number" == typeof t[c + 1]) {
            if (((a = t[c]), null != r && a >= r)) break;
          } else
            t[c] < 0 && (e[Hr] += 65536),
              (a < o || -1 == o) &&
                (sS(e, n, t, c), (e[Hr] = (4294901760 & e[Hr]) + c + 2)),
              c++;
      }
      function og(e, t) {
        Jt(4, e, t);
        const n = Mt(null);
        try {
          t.call(e);
        } finally {
          Mt(n), Jt(5, e, t);
        }
      }
      function sS(e, t, n, r) {
        const i = n[r] < 0,
          o = n[r + 1],
          a = e[i ? -n[r] : n[r]];
        i
          ? e[V] >> 13 < e[Hr] >> 16 &&
            (3 & e[V]) === t &&
            ((e[V] += 8192), og(a, o))
          : og(a, o);
      }
      const Zr = -1;
      class bo {
        constructor(t, n, r) {
          (this.factory = t),
            (this.resolving = !1),
            (this.canSeeViewProviders = n),
            (this.injectImpl = r);
        }
      }
      function Cu(e) {
        return e !== Zr;
      }
      function yo(e) {
        return 32767 & e;
      }
      function vo(e, t) {
        let n = (function uS(e) {
            return e >> 16;
          })(e),
          r = t;
        for (; n > 0; ) (r = r[Ur]), n--;
        return r;
      }
      let Iu = !0;
      function ca(e) {
        const t = Iu;
        return (Iu = e), t;
      }
      const sg = 255,
        ag = 5;
      let dS = 0;
      const tn = {};
      function la(e, t) {
        const n = cg(e, t);
        if (-1 !== n) return n;
        const r = t[I];
        r.firstCreatePass &&
          ((e.injectorIndex = t.length),
          Mu(r.data, e),
          Mu(t, null),
          Mu(r.blueprint, null));
        const i = ua(e, t),
          o = e.injectorIndex;
        if (Cu(i)) {
          const s = yo(i),
            a = vo(i, t),
            c = a[I].data;
          for (let l = 0; l < 8; l++) t[o + l] = a[s + l] | c[s + l];
        }
        return (t[o + 8] = i), o;
      }
      function Mu(e, t) {
        e.push(0, 0, 0, 0, 0, 0, 0, 0, t);
      }
      function cg(e, t) {
        return -1 === e.injectorIndex ||
          (e.parent && e.parent.injectorIndex === e.injectorIndex) ||
          null === t[e.injectorIndex + 8]
          ? -1
          : e.injectorIndex;
      }
      function ua(e, t) {
        if (e.parent && -1 !== e.parent.injectorIndex)
          return e.parent.injectorIndex;
        let n = 0,
          r = null,
          i = t;
        for (; null !== i; ) {
          if (((r = gg(i)), null === r)) return Zr;
          if ((n++, (i = i[Ur]), -1 !== r.injectorIndex))
            return r.injectorIndex | (n << 16);
        }
        return Zr;
      }
      function Su(e, t, n) {
        !(function fS(e, t, n) {
          let r;
          "string" == typeof n
            ? (r = n.charCodeAt(0) || 0)
            : n.hasOwnProperty(oo) && (r = n[oo]),
            null == r && (r = n[oo] = dS++);
          const i = r & sg;
          t.data[e + (i >> ag)] |= 1 << i;
        })(e, t, n);
      }
      function lg(e, t, n) {
        if (n & H.Optional || void 0 !== e) return e;
        Wl();
      }
      function ug(e, t, n, r) {
        if (
          (n & H.Optional && void 0 === r && (r = null),
          !(n & (H.Self | H.Host)))
        ) {
          const i = e[jn],
            o = tt(void 0);
          try {
            return i ? i.get(t, r, n & H.Optional) : Xp(t, r, n & H.Optional);
          } finally {
            tt(o);
          }
        }
        return lg(r, 0, n);
      }
      function dg(e, t, n, r = H.Default, i) {
        if (null !== e) {
          if (2048 & t[V] && !(r & H.Self)) {
            const s = (function yS(e, t, n, r, i) {
              let o = e,
                s = t;
              for (
                ;
                null !== o && null !== s && 2048 & s[V] && !(512 & s[V]);

              ) {
                const a = fg(o, s, n, r | H.Self, tn);
                if (a !== tn) return a;
                let c = o.parent;
                if (!c) {
                  const l = s[gm];
                  if (l) {
                    const u = l.get(n, tn, r);
                    if (u !== tn) return u;
                  }
                  (c = gg(s)), (s = s[Ur]);
                }
                o = c;
              }
              return i;
            })(e, t, n, r, tn);
            if (s !== tn) return s;
          }
          const o = fg(e, t, n, r, tn);
          if (o !== tn) return o;
        }
        return ug(t, n, r, i);
      }
      function fg(e, t, n, r, i) {
        const o = (function mS(e) {
          if ("string" == typeof e) return e.charCodeAt(0) || 0;
          const t = e.hasOwnProperty(oo) ? e[oo] : void 0;
          return "number" == typeof t ? (t >= 0 ? t & sg : bS) : t;
        })(n);
        if ("function" == typeof o) {
          if (!Ym(t, e, r)) return r & H.Host ? lg(i, 0, r) : ug(t, n, r, i);
          try {
            let s;
            if (((s = o(r)), null != s || r & H.Optional)) return s;
            Wl();
          } finally {
            tg();
          }
        } else if ("number" == typeof o) {
          let s = null,
            a = cg(e, t),
            c = Zr,
            l = r & H.Host ? t[ve][Ve] : null;
          for (
            (-1 === a || r & H.SkipSelf) &&
            ((c = -1 === a ? ua(e, t) : t[a + 8]),
            c !== Zr && pg(r, !1)
              ? ((s = t[I]), (a = yo(c)), (t = vo(c, t)))
              : (a = -1));
            -1 !== a;

          ) {
            const u = t[I];
            if (hg(o, a, u.data)) {
              const d = pS(a, t, n, s, r, l);
              if (d !== tn) return d;
            }
            (c = t[a + 8]),
              c !== Zr && pg(r, t[I].data[a + 8] === l) && hg(o, a, t)
                ? ((s = u), (a = yo(c)), (t = vo(c, t)))
                : (a = -1);
          }
        }
        return i;
      }
      function pS(e, t, n, r, i, o) {
        const s = t[I],
          a = s.data[e + 8],
          u = (function da(e, t, n, r, i) {
            const o = e.providerIndexes,
              s = t.data,
              a = 1048575 & o,
              c = e.directiveStart,
              u = o >> 20,
              f = i ? a + u : e.directiveEnd;
            for (let h = r ? a : a + u; h < f; h++) {
              const p = s[h];
              if ((h < c && n === p) || (h >= c && p.type === n)) return h;
            }
            if (i) {
              const h = s[c];
              if (h && Bt(h) && h.type === n) return c;
            }
            return null;
          })(
            a,
            s,
            n,
            null == r ? sr(a) && Iu : r != s && 0 != (3 & a.type),
            i & H.Host && o === a,
          );
        return null !== u ? ur(t, s, u, a) : tn;
      }
      function ur(e, t, n, r) {
        let i = e[n];
        const o = t.data;
        if (
          (function aS(e) {
            return e instanceof bo;
          })(i)
        ) {
          const s = i;
          s.resolving &&
            (function PI(e, t) {
              const n = t ? `. Dependency path: ${t.join(" > ")} > ${e}` : "";
              throw new v(
                -200,
                `Circular dependency in DI detected for ${e}${n}`,
              );
            })(
              (function X(e) {
                return "function" == typeof e
                  ? e.name || e.toString()
                  : "object" == typeof e &&
                    null != e &&
                    "function" == typeof e.type
                  ? e.type.name || e.type.toString()
                  : L(e);
              })(o[n]),
            );
          const a = ca(s.canSeeViewProviders);
          s.resolving = !0;
          const l = s.injectImpl ? tt(s.injectImpl) : null;
          Ym(e, r, H.Default);
          try {
            (i = e[n] = s.factory(void 0, o, e, r)),
              t.firstCreatePass &&
                n >= r.directiveStart &&
                (function oS(e, t, n) {
                  const {
                    ngOnChanges: r,
                    ngOnInit: i,
                    ngDoCheck: o,
                  } = t.type.prototype;
                  if (r) {
                    const s = Pm(t);
                    (n.preOrderHooks ??= []).push(e, s),
                      (n.preOrderCheckHooks ??= []).push(e, s);
                  }
                  i && (n.preOrderHooks ??= []).push(0 - e, i),
                    o &&
                      ((n.preOrderHooks ??= []).push(e, o),
                      (n.preOrderCheckHooks ??= []).push(e, o));
                })(n, o[n], t);
          } finally {
            null !== l && tt(l), ca(a), (s.resolving = !1), tg();
          }
        }
        return i;
      }
      function hg(e, t, n) {
        return !!(n[t + (e >> ag)] & (1 << e));
      }
      function pg(e, t) {
        return !(e & H.Self || (e & H.Host && t));
      }
      class Qe {
        constructor(t, n) {
          (this._tNode = t), (this._lView = n);
        }
        get(t, n, r) {
          return dg(this._tNode, this._lView, t, Zs(r), n);
        }
      }
      function bS() {
        return new Qe(ke(), _());
      }
      function xu(e) {
        return ql(e)
          ? () => {
              const t = xu(k(e));
              return t && t();
            }
          : ar(e);
      }
      function gg(e) {
        const t = e[I],
          n = t.type;
        return 2 === n ? t.declTNode : 1 === n ? e[Ve] : null;
      }
      const Yr = "__parameters__";
      function Jr(e, t, n) {
        return mn(() => {
          const r = (function Tu(e) {
            return function (...n) {
              if (e) {
                const r = e(...n);
                for (const i in r) this[i] = r[i];
              }
            };
          })(t);
          function i(...o) {
            if (this instanceof i) return r.apply(this, o), this;
            const s = new i(...o);
            return (a.annotation = s), a;
            function a(c, l, u) {
              const d = c.hasOwnProperty(Yr)
                ? c[Yr]
                : Object.defineProperty(c, Yr, { value: [] })[Yr];
              for (; d.length <= u; ) d.push(null);
              return (d[u] = d[u] || []).push(s), c;
            }
          }
          return (
            n && (i.prototype = Object.create(n.prototype)),
            (i.prototype.ngMetadataName = e),
            (i.annotationCls = i),
            i
          );
        });
      }
      function ti(e, t) {
        e.forEach((n) => (Array.isArray(n) ? ti(n, t) : t(n)));
      }
      function yg(e, t, n) {
        t >= e.length ? e.push(n) : e.splice(t, 0, n);
      }
      function fa(e, t) {
        return t >= e.length - 1 ? e.pop() : e.splice(t, 1)[0];
      }
      function Eo(e, t) {
        const n = [];
        for (let r = 0; r < e; r++) n.push(t);
        return n;
      }
      function ht(e, t, n) {
        let r = ni(e, t);
        return (
          r >= 0
            ? (e[1 | r] = n)
            : ((r = ~r),
              (function IS(e, t, n, r) {
                let i = e.length;
                if (i == t) e.push(n, r);
                else if (1 === i) e.push(r, e[0]), (e[0] = n);
                else {
                  for (i--, e.push(e[i - 1], e[i]); i > t; )
                    (e[i] = e[i - 2]), i--;
                  (e[t] = n), (e[t + 1] = r);
                }
              })(e, r, t, n)),
          r
        );
      }
      function Au(e, t) {
        const n = ni(e, t);
        if (n >= 0) return e[1 | n];
      }
      function ni(e, t) {
        return (function vg(e, t, n) {
          let r = 0,
            i = e.length >> n;
          for (; i !== r; ) {
            const o = r + ((i - r) >> 1),
              s = e[o << n];
            if (t === s) return o << n;
            s > t ? (i = o) : (r = o + 1);
          }
          return ~(i << n);
        })(e, t, 1);
      }
      const dr = io(Jr("Optional"), 8),
        Co = io(Jr("SkipSelf"), 4);
      function ya(e) {
        return 128 == (128 & e.flags);
      }
      var Hn = (function (e) {
        return (
          (e[(e.Important = 1)] = "Important"),
          (e[(e.DashCase = 2)] = "DashCase"),
          e
        );
      })(Hn || {});
      const ku = new Map();
      let ZS = 0;
      const Lu = "__ngContext__";
      function $e(e, t) {
        rt(t)
          ? ((e[Lu] = t[uo]),
            (function YS(e) {
              ku.set(e[uo], e);
            })(t))
          : (e[Lu] = t);
      }
      let ju;
      function Bu(e, t) {
        return ju(e, t);
      }
      function So(e) {
        const t = e[de];
        return We(t) ? t[de] : t;
      }
      function Bg(e) {
        return $g(e[co]);
      }
      function Vg(e) {
        return $g(e[jt]);
      }
      function $g(e) {
        for (; null !== e && !We(e); ) e = e[jt];
        return e;
      }
      function oi(e, t, n, r, i) {
        if (null != r) {
          let o,
            s = !1;
          We(r) ? (o = r) : rt(r) && ((s = !0), (r = r[me]));
          const a = se(r);
          0 === e && null !== n
            ? null == i
              ? qg(t, n, a)
              : fr(t, n, a, i || null, !0)
            : 1 === e && null !== n
            ? fr(t, n, a, i || null, !0)
            : 2 === e
            ? (function Ia(e, t, n) {
                const r = Ea(e, t);
                r &&
                  (function gx(e, t, n, r) {
                    e.removeChild(t, n, r);
                  })(e, r, t, n);
              })(t, a, s)
            : 3 === e && t.destroyNode(a),
            null != o &&
              (function vx(e, t, n, r, i) {
                const o = n[Xt];
                o !== se(n) && oi(t, e, r, o, i);
                for (let a = Oe; a < n.length; a++) {
                  const c = n[a];
                  To(c[I], c, e, t, r, o);
                }
              })(t, e, o, n, i);
        }
      }
      function Da(e, t, n) {
        return e.createElement(t, n);
      }
      function Hg(e, t) {
        const n = e[zr],
          r = n.indexOf(t);
        $m(t), n.splice(r, 1);
      }
      function wa(e, t) {
        if (e.length <= Oe) return;
        const n = Oe + t,
          r = e[n];
        if (r) {
          const i = r[lo];
          null !== i && i !== e && Hg(i, r), t > 0 && (e[n - 1][jt] = r[jt]);
          const o = fa(e, Oe + t);
          !(function cx(e, t) {
            To(e, t, t[j], 2, null, null), (t[me] = null), (t[Ve] = null);
          })(r[I], r);
          const s = o[Yt];
          null !== s && s.detachView(o[I]),
            (r[de] = null),
            (r[jt] = null),
            (r[V] &= -129);
        }
        return r;
      }
      function $u(e, t) {
        if (!(256 & t[V])) {
          const n = t[j];
          t[fo] && Mm(t[fo]),
            t[ho] && Mm(t[ho]),
            n.destroyNode && To(e, t, n, 3, null, null),
            (function dx(e) {
              let t = e[co];
              if (!t) return Uu(e[I], e);
              for (; t; ) {
                let n = null;
                if (rt(t)) n = t[co];
                else {
                  const r = t[Oe];
                  r && (n = r);
                }
                if (!n) {
                  for (; t && !t[jt] && t !== e; )
                    rt(t) && Uu(t[I], t), (t = t[de]);
                  null === t && (t = e), rt(t) && Uu(t[I], t), (n = t && t[jt]);
                }
                t = n;
              }
            })(t);
        }
      }
      function Uu(e, t) {
        if (!(256 & t[V])) {
          (t[V] &= -129),
            (t[V] |= 256),
            (function mx(e, t) {
              let n;
              if (null != e && null != (n = e.destroyHooks))
                for (let r = 0; r < n.length; r += 2) {
                  const i = t[n[r]];
                  if (!(i instanceof bo)) {
                    const o = n[r + 1];
                    if (Array.isArray(o))
                      for (let s = 0; s < o.length; s += 2) {
                        const a = i[o[s]],
                          c = o[s + 1];
                        Jt(4, a, c);
                        try {
                          c.call(a);
                        } finally {
                          Jt(5, a, c);
                        }
                      }
                    else {
                      Jt(4, i, o);
                      try {
                        o.call(i);
                      } finally {
                        Jt(5, i, o);
                      }
                    }
                  }
                }
            })(e, t),
            (function px(e, t) {
              const n = e.cleanup,
                r = t[Vr];
              if (null !== n)
                for (let o = 0; o < n.length - 1; o += 2)
                  if ("string" == typeof n[o]) {
                    const s = n[o + 3];
                    s >= 0 ? r[s]() : r[-s].unsubscribe(), (o += 2);
                  } else n[o].call(r[n[o + 1]]);
              null !== r && (t[Vr] = null);
              const i = t[Bn];
              if (null !== i) {
                t[Bn] = null;
                for (let o = 0; o < i.length; o++) (0, i[o])();
              }
            })(e, t),
            1 === t[I].type && t[j].destroy();
          const n = t[lo];
          if (null !== n && We(t[de])) {
            n !== t[de] && Hg(n, t);
            const r = t[Yt];
            null !== r && r.detachView(e);
          }
          !(function XS(e) {
            ku.delete(e[uo]);
          })(t);
        }
      }
      function Hu(e, t, n) {
        return (function zg(e, t, n) {
          let r = t;
          for (; null !== r && 40 & r.type; ) r = (t = r).parent;
          if (null === r) return n[me];
          {
            const { componentOffset: i } = r;
            if (i > -1) {
              const { encapsulation: o } = e.data[r.directiveStart + i];
              if (o === It.None || o === It.Emulated) return null;
            }
            return it(r, n);
          }
        })(e, t.parent, n);
      }
      function fr(e, t, n, r, i) {
        e.insertBefore(t, n, r, i);
      }
      function qg(e, t, n) {
        e.appendChild(t, n);
      }
      function Gg(e, t, n, r, i) {
        null !== r ? fr(e, t, n, r, i) : qg(e, t, n);
      }
      function Ea(e, t) {
        return e.parentNode(t);
      }
      function Wg(e, t, n) {
        return Zg(e, t, n);
      }
      let zu,
        Ma,
        Ku,
        Zg = function Kg(e, t, n) {
          return 40 & e.type ? it(e, n) : null;
        };
      function Ca(e, t, n, r) {
        const i = Hu(e, r, t),
          o = t[j],
          a = Wg(r.parent || t[Ve], r, t);
        if (null != i)
          if (Array.isArray(n))
            for (let c = 0; c < n.length; c++) Gg(o, i, n[c], a, !1);
          else Gg(o, i, n, a, !1);
        void 0 !== zu && zu(o, r, t, n, i);
      }
      function xo(e, t) {
        if (null !== t) {
          const n = t.type;
          if (3 & n) return it(t, e);
          if (4 & n) return qu(-1, e[t.index]);
          if (8 & n) {
            const r = t.child;
            if (null !== r) return xo(e, r);
            {
              const i = e[t.index];
              return We(i) ? qu(-1, i) : se(i);
            }
          }
          if (32 & n) return Bu(t, e)() || se(e[t.index]);
          {
            const r = Yg(e, t);
            return null !== r
              ? Array.isArray(r)
                ? r[0]
                : xo(So(e[ve]), r)
              : xo(e, t.next);
          }
        }
        return null;
      }
      function Yg(e, t) {
        return null !== t ? e[ve][Ve].projection[t.projection] : null;
      }
      function qu(e, t) {
        const n = Oe + e + 1;
        if (n < t.length) {
          const r = t[n],
            i = r[I].firstChild;
          if (null !== i) return xo(r, i);
        }
        return t[Xt];
      }
      function Gu(e, t, n, r, i, o, s) {
        for (; null != n; ) {
          const a = r[n.index],
            c = n.type;
          if (
            (s && 0 === t && (a && $e(se(a), r), (n.flags |= 2)),
            32 != (32 & n.flags))
          )
            if (8 & c) Gu(e, t, n.child, r, i, o, !1), oi(t, e, i, a, o);
            else if (32 & c) {
              const l = Bu(n, r);
              let u;
              for (; (u = l()); ) oi(t, e, i, u, o);
              oi(t, e, i, a, o);
            } else 16 & c ? Jg(e, t, r, n, i, o) : oi(t, e, i, a, o);
          n = s ? n.projectionNext : n.next;
        }
      }
      function To(e, t, n, r, i, o) {
        Gu(n, r, e.firstChild, t, i, o, !1);
      }
      function Jg(e, t, n, r, i, o) {
        const s = n[ve],
          c = s[Ve].projection[r.projection];
        if (Array.isArray(c))
          for (let l = 0; l < c.length; l++) oi(t, e, i, c[l], o);
        else {
          let l = c;
          const u = s[de];
          ya(r) && (l.flags |= 128), Gu(e, t, l, u, i, o, !0);
        }
      }
      function eb(e, t, n) {
        "" === n
          ? e.removeAttribute(t, "class")
          : e.setAttribute(t, "class", n);
      }
      function tb(e, t, n) {
        const { mergedAttrs: r, classes: i, styles: o } = n;
        null !== r && iu(e, t, r),
          null !== i && eb(e, t, i),
          null !== o &&
            (function Dx(e, t, n) {
              e.setAttribute(t, "style", n);
            })(e, t, o);
      }
      function si(e) {
        return (
          (function Wu() {
            if (void 0 === Ma && ((Ma = null), oe.trustedTypes))
              try {
                Ma = oe.trustedTypes.createPolicy("angular", {
                  createHTML: (e) => e,
                  createScript: (e) => e,
                  createScriptURL: (e) => e,
                });
              } catch {}
            return Ma;
          })()?.createHTML(e) || e
        );
      }
      class hr {
        constructor(t) {
          this.changingThisBreaksApplicationSecurity = t;
        }
        toString() {
          return `SafeValue must use [property]=binding: ${this.changingThisBreaksApplicationSecurity} (see ${Kp})`;
        }
      }
      class Mx extends hr {
        getTypeName() {
          return "HTML";
        }
      }
      class Sx extends hr {
        getTypeName() {
          return "Style";
        }
      }
      class xx extends hr {
        getTypeName() {
          return "Script";
        }
      }
      class Tx extends hr {
        getTypeName() {
          return "URL";
        }
      }
      class Ax extends hr {
        getTypeName() {
          return "ResourceURL";
        }
      }
      function pt(e) {
        return e instanceof hr ? e.changingThisBreaksApplicationSecurity : e;
      }
      function nn(e, t) {
        const n = (function Nx(e) {
          return (e instanceof hr && e.getTypeName()) || null;
        })(e);
        if (null != n && n !== t) {
          if ("ResourceURL" === n && "URL" === t) return !0;
          throw new Error(`Required a safe ${t}, got a ${n} (see ${Kp})`);
        }
        return n === t;
      }
      class Lx {
        constructor(t) {
          this.inertDocumentHelper = t;
        }
        getInertBodyElement(t) {
          t = "<body><remove></remove>" + t;
          try {
            const n = new window.DOMParser().parseFromString(
              si(t),
              "text/html",
            ).body;
            return null === n
              ? this.inertDocumentHelper.getInertBodyElement(t)
              : (n.removeChild(n.firstChild), n);
          } catch {
            return null;
          }
        }
      }
      class jx {
        constructor(t) {
          (this.defaultDoc = t),
            (this.inertDocument =
              this.defaultDoc.implementation.createHTMLDocument(
                "sanitization-inert",
              ));
        }
        getInertBodyElement(t) {
          const n = this.inertDocument.createElement("template");
          return (n.innerHTML = si(t)), n;
        }
      }
      const Vx = /^(?!javascript:)(?:[a-z0-9+.-]+:|[^&:\/?#]*(?:[\/?#]|$))/i;
      function xa(e) {
        return (e = String(e)).match(Vx) ? e : "unsafe:" + e;
      }
      function Dn(e) {
        const t = {};
        for (const n of e.split(",")) t[n] = !0;
        return t;
      }
      function Ao(...e) {
        const t = {};
        for (const n of e)
          for (const r in n) n.hasOwnProperty(r) && (t[r] = !0);
        return t;
      }
      const sb = Dn("area,br,col,hr,img,wbr"),
        ab = Dn("colgroup,dd,dt,li,p,tbody,td,tfoot,th,thead,tr"),
        cb = Dn("rp,rt"),
        Qu = Ao(
          sb,
          Ao(
            ab,
            Dn(
              "address,article,aside,blockquote,caption,center,del,details,dialog,dir,div,dl,figure,figcaption,footer,h1,h2,h3,h4,h5,h6,header,hgroup,hr,ins,main,map,menu,nav,ol,pre,section,summary,table,ul",
            ),
          ),
          Ao(
            cb,
            Dn(
              "a,abbr,acronym,audio,b,bdi,bdo,big,br,cite,code,del,dfn,em,font,i,img,ins,kbd,label,map,mark,picture,q,ruby,rp,rt,s,samp,small,source,span,strike,strong,sub,sup,time,track,tt,u,var,video",
            ),
          ),
          Ao(cb, ab),
        ),
        Yu = Dn("background,cite,href,itemtype,longdesc,poster,src,xlink:href"),
        lb = Ao(
          Yu,
          Dn(
            "abbr,accesskey,align,alt,autoplay,axis,bgcolor,border,cellpadding,cellspacing,class,clear,color,cols,colspan,compact,controls,coords,datetime,default,dir,download,face,headers,height,hidden,hreflang,hspace,ismap,itemscope,itemprop,kind,label,lang,language,loop,media,muted,nohref,nowrap,open,preload,rel,rev,role,rows,rowspan,rules,scope,scrolling,shape,size,sizes,span,srclang,srcset,start,summary,tabindex,target,title,translate,type,usemap,valign,value,vspace,width",
          ),
          Dn(
            "aria-activedescendant,aria-atomic,aria-autocomplete,aria-busy,aria-checked,aria-colcount,aria-colindex,aria-colspan,aria-controls,aria-current,aria-describedby,aria-details,aria-disabled,aria-dropeffect,aria-errormessage,aria-expanded,aria-flowto,aria-grabbed,aria-haspopup,aria-hidden,aria-invalid,aria-keyshortcuts,aria-label,aria-labelledby,aria-level,aria-live,aria-modal,aria-multiline,aria-multiselectable,aria-orientation,aria-owns,aria-placeholder,aria-posinset,aria-pressed,aria-readonly,aria-relevant,aria-required,aria-roledescription,aria-rowcount,aria-rowindex,aria-rowspan,aria-selected,aria-setsize,aria-sort,aria-valuemax,aria-valuemin,aria-valuenow,aria-valuetext",
          ),
        ),
        $x = Dn("script,style,template");
      class Ux {
        constructor() {
          (this.sanitizedSomething = !1), (this.buf = []);
        }
        sanitizeChildren(t) {
          let n = t.firstChild,
            r = !0;
          for (; n; )
            if (
              (n.nodeType === Node.ELEMENT_NODE
                ? (r = this.startElement(n))
                : n.nodeType === Node.TEXT_NODE
                ? this.chars(n.nodeValue)
                : (this.sanitizedSomething = !0),
              r && n.firstChild)
            )
              n = n.firstChild;
            else
              for (; n; ) {
                n.nodeType === Node.ELEMENT_NODE && this.endElement(n);
                let i = this.checkClobberedElement(n, n.nextSibling);
                if (i) {
                  n = i;
                  break;
                }
                n = this.checkClobberedElement(n, n.parentNode);
              }
          return this.buf.join("");
        }
        startElement(t) {
          const n = t.nodeName.toLowerCase();
          if (!Qu.hasOwnProperty(n))
            return (this.sanitizedSomething = !0), !$x.hasOwnProperty(n);
          this.buf.push("<"), this.buf.push(n);
          const r = t.attributes;
          for (let i = 0; i < r.length; i++) {
            const o = r.item(i),
              s = o.name,
              a = s.toLowerCase();
            if (!lb.hasOwnProperty(a)) {
              this.sanitizedSomething = !0;
              continue;
            }
            let c = o.value;
            Yu[a] && (c = xa(c)), this.buf.push(" ", s, '="', ub(c), '"');
          }
          return this.buf.push(">"), !0;
        }
        endElement(t) {
          const n = t.nodeName.toLowerCase();
          Qu.hasOwnProperty(n) &&
            !sb.hasOwnProperty(n) &&
            (this.buf.push("</"), this.buf.push(n), this.buf.push(">"));
        }
        chars(t) {
          this.buf.push(ub(t));
        }
        checkClobberedElement(t, n) {
          if (
            n &&
            (t.compareDocumentPosition(n) &
              Node.DOCUMENT_POSITION_CONTAINED_BY) ===
              Node.DOCUMENT_POSITION_CONTAINED_BY
          )
            throw new Error(
              `Failed to sanitize html because the element is clobbered: ${t.outerHTML}`,
            );
          return n;
        }
      }
      const Hx = /[\uD800-\uDBFF][\uDC00-\uDFFF]/g,
        zx = /([^\#-~ |!])/g;
      function ub(e) {
        return e
          .replace(/&/g, "&amp;")
          .replace(Hx, function (t) {
            return (
              "&#" +
              (1024 * (t.charCodeAt(0) - 55296) +
                (t.charCodeAt(1) - 56320) +
                65536) +
              ";"
            );
          })
          .replace(zx, function (t) {
            return "&#" + t.charCodeAt(0) + ";";
          })
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;");
      }
      let Ta;
      function db(e, t) {
        let n = null;
        try {
          Ta =
            Ta ||
            (function ob(e) {
              const t = new jx(e);
              return (function Bx() {
                try {
                  return !!new window.DOMParser().parseFromString(
                    si(""),
                    "text/html",
                  );
                } catch {
                  return !1;
                }
              })()
                ? new Lx(t)
                : t;
            })(e);
          let r = t ? String(t) : "";
          n = Ta.getInertBodyElement(r);
          let i = 5,
            o = r;
          do {
            if (0 === i)
              throw new Error(
                "Failed to sanitize html because the input is unstable",
              );
            i--, (r = o), (o = n.innerHTML), (n = Ta.getInertBodyElement(r));
          } while (r !== o);
          return si(new Ux().sanitizeChildren(Xu(n) || n));
        } finally {
          if (n) {
            const r = Xu(n) || n;
            for (; r.firstChild; ) r.removeChild(r.firstChild);
          }
        }
      }
      function Xu(e) {
        return "content" in e &&
          (function qx(e) {
            return (
              e.nodeType === Node.ELEMENT_NODE && "TEMPLATE" === e.nodeName
            );
          })(e)
          ? e.content
          : null;
      }
      var Fe = (function (e) {
        return (
          (e[(e.NONE = 0)] = "NONE"),
          (e[(e.HTML = 1)] = "HTML"),
          (e[(e.STYLE = 2)] = "STYLE"),
          (e[(e.SCRIPT = 3)] = "SCRIPT"),
          (e[(e.URL = 4)] = "URL"),
          (e[(e.RESOURCE_URL = 5)] = "RESOURCE_URL"),
          e
        );
      })(Fe || {});
      const Ro = new E("ENVIRONMENT_INITIALIZER"),
        mb = new E("INJECTOR", -1),
        gb = new E("INJECTOR_DEF_TYPES");
      class Ju {
        get(t, n = ro) {
          if (n === ro) {
            const r = new Error(`NullInjectorError: No provider for ${Ce(t)}!`);
            throw ((r.name = "NullInjectorError"), r);
          }
          return n;
        }
      }
      function Xx(...e) {
        return { ɵproviders: bb(0, e), ɵfromNgModule: !0 };
      }
      function bb(e, ...t) {
        const n = [],
          r = new Set();
        let i;
        const o = (s) => {
          n.push(s);
        };
        return (
          ti(t, (s) => {
            const a = s;
            Aa(a, o, [], r) && ((i ||= []), i.push(a));
          }),
          void 0 !== i && yb(i, o),
          n
        );
      }
      function yb(e, t) {
        for (let n = 0; n < e.length; n++) {
          const { ngModule: r, providers: i } = e[n];
          td(i, (o) => {
            t(o, r);
          });
        }
      }
      function Aa(e, t, n, r) {
        if (!(e = k(e))) return !1;
        let i = null,
          o = Gs(e);
        const s = !o && q(e);
        if (o || s) {
          if (s && !s.standalone) return !1;
          i = e;
        } else {
          const c = e.ngModule;
          if (((o = Gs(c)), !o)) return !1;
          i = c;
        }
        const a = r.has(i);
        if (s) {
          if (a) return !1;
          if ((r.add(i), s.dependencies)) {
            const c =
              "function" == typeof s.dependencies
                ? s.dependencies()
                : s.dependencies;
            for (const l of c) Aa(l, t, n, r);
          }
        } else {
          if (!o) return !1;
          {
            if (null != o.imports && !a) {
              let l;
              r.add(i);
              try {
                ti(o.imports, (u) => {
                  Aa(u, t, n, r) && ((l ||= []), l.push(u));
                });
              } finally {
              }
              void 0 !== l && yb(l, t);
            }
            if (!a) {
              const l = ar(i) || (() => new i());
              t({ provide: i, useFactory: l, deps: Z }, i),
                t({ provide: gb, useValue: i, multi: !0 }, i),
                t({ provide: Ro, useValue: () => D(i), multi: !0 }, i);
            }
            const c = o.providers;
            if (null != c && !a) {
              const l = e;
              td(c, (u) => {
                t(u, l);
              });
            }
          }
        }
        return i !== e && void 0 !== e.providers;
      }
      function td(e, t) {
        for (let n of e)
          Gl(n) && (n = n.ɵproviders), Array.isArray(n) ? td(n, t) : t(n);
      }
      const Jx = J({ provide: String, useValue: J });
      function nd(e) {
        return null !== e && "object" == typeof e && Jx in e;
      }
      function pr(e) {
        return "function" == typeof e;
      }
      const rd = new E("Set Injector scope."),
        Na = {},
        tT = {};
      let id;
      function Ra() {
        return void 0 === id && (id = new Ju()), id;
      }
      class mt {}
      class ci extends mt {
        get destroyed() {
          return this._destroyed;
        }
        constructor(t, n, r, i) {
          super(),
            (this.parent = n),
            (this.source = r),
            (this.scopes = i),
            (this.records = new Map()),
            (this._ngOnDestroyHooks = new Set()),
            (this._onDestroyHooks = []),
            (this._destroyed = !1),
            sd(t, (s) => this.processProvider(s)),
            this.records.set(mb, li(void 0, this)),
            i.has("environment") && this.records.set(mt, li(void 0, this));
          const o = this.records.get(rd);
          null != o && "string" == typeof o.value && this.scopes.add(o.value),
            (this.injectorDefTypes = new Set(this.get(gb.multi, Z, H.Self)));
        }
        destroy() {
          this.assertNotDestroyed(), (this._destroyed = !0);
          try {
            for (const n of this._ngOnDestroyHooks) n.ngOnDestroy();
            const t = this._onDestroyHooks;
            this._onDestroyHooks = [];
            for (const n of t) n();
          } finally {
            this.records.clear(),
              this._ngOnDestroyHooks.clear(),
              this.injectorDefTypes.clear();
          }
        }
        onDestroy(t) {
          return (
            this.assertNotDestroyed(),
            this._onDestroyHooks.push(t),
            () => this.removeOnDestroy(t)
          );
        }
        runInContext(t) {
          this.assertNotDestroyed();
          const n = Ln(this),
            r = tt(void 0);
          try {
            return t();
          } finally {
            Ln(n), tt(r);
          }
        }
        get(t, n = ro, r = H.Default) {
          if ((this.assertNotDestroyed(), t.hasOwnProperty(rm)))
            return t[rm](this);
          r = Zs(r);
          const o = Ln(this),
            s = tt(void 0);
          try {
            if (!(r & H.SkipSelf)) {
              let c = this.records.get(t);
              if (void 0 === c) {
                const l =
                  (function sT(e) {
                    return (
                      "function" == typeof e ||
                      ("object" == typeof e && e instanceof E)
                    );
                  })(t) && qs(t);
                (c = l && this.injectableDefInScope(l) ? li(od(t), Na) : null),
                  this.records.set(t, c);
              }
              if (null != c) return this.hydrate(t, c);
            }
            return (r & H.Self ? Ra() : this.parent).get(
              t,
              (n = r & H.Optional && n === ro ? null : n),
            );
          } catch (a) {
            if ("NullInjectorError" === a.name) {
              if (((a[Ks] = a[Ks] || []).unshift(Ce(t)), o)) throw a;
              return (function ZI(e, t, n, r) {
                const i = e[Ks];
                throw (
                  (t[em] && i.unshift(t[em]),
                  (e.message = (function QI(e, t, n, r = null) {
                    e =
                      e && "\n" === e.charAt(0) && "\u0275" == e.charAt(1)
                        ? e.slice(2)
                        : e;
                    let i = Ce(t);
                    if (Array.isArray(t)) i = t.map(Ce).join(" -> ");
                    else if ("object" == typeof t) {
                      let o = [];
                      for (let s in t)
                        if (t.hasOwnProperty(s)) {
                          let a = t[s];
                          o.push(
                            s +
                              ":" +
                              ("string" == typeof a
                                ? JSON.stringify(a)
                                : Ce(a)),
                          );
                        }
                      i = `{${o.join(", ")}}`;
                    }
                    return `${n}${r ? "(" + r + ")" : ""}[${i}]: ${e.replace(
                      zI,
                      "\n  ",
                    )}`;
                  })("\n" + e.message, i, n, r)),
                  (e.ngTokenPath = i),
                  (e[Ks] = null),
                  e)
                );
              })(a, t, "R3InjectorError", this.source);
            }
            throw a;
          } finally {
            tt(s), Ln(o);
          }
        }
        resolveInjectorInitializers() {
          const t = Ln(this),
            n = tt(void 0);
          try {
            const i = this.get(Ro.multi, Z, H.Self);
            for (const o of i) o();
          } finally {
            Ln(t), tt(n);
          }
        }
        toString() {
          const t = [],
            n = this.records;
          for (const r of n.keys()) t.push(Ce(r));
          return `R3Injector[${t.join(", ")}]`;
        }
        assertNotDestroyed() {
          if (this._destroyed) throw new v(205, !1);
        }
        processProvider(t) {
          let n = pr((t = k(t))) ? t : k(t && t.provide);
          const r = (function rT(e) {
            return nd(e)
              ? li(void 0, e.useValue)
              : li(
                  (function Db(e, t, n) {
                    let r;
                    if (pr(e)) {
                      const i = k(e);
                      return ar(i) || od(i);
                    }
                    if (nd(e)) r = () => k(e.useValue);
                    else if (
                      (function _b(e) {
                        return !(!e || !e.useFactory);
                      })(e)
                    )
                      r = () => e.useFactory(...tu(e.deps || []));
                    else if (
                      (function vb(e) {
                        return !(!e || !e.useExisting);
                      })(e)
                    )
                      r = () => D(k(e.useExisting));
                    else {
                      const i = k(e && (e.useClass || e.provide));
                      if (
                        !(function iT(e) {
                          return !!e.deps;
                        })(e)
                      )
                        return ar(i) || od(i);
                      r = () => new i(...tu(e.deps));
                    }
                    return r;
                  })(e),
                  Na,
                );
          })(t);
          if (pr(t) || !0 !== t.multi) this.records.get(n);
          else {
            let i = this.records.get(n);
            i ||
              ((i = li(void 0, Na, !0)),
              (i.factory = () => tu(i.multi)),
              this.records.set(n, i)),
              (n = t),
              i.multi.push(t);
          }
          this.records.set(n, r);
        }
        hydrate(t, n) {
          return (
            n.value === Na && ((n.value = tT), (n.value = n.factory())),
            "object" == typeof n.value &&
              n.value &&
              (function oT(e) {
                return (
                  null !== e &&
                  "object" == typeof e &&
                  "function" == typeof e.ngOnDestroy
                );
              })(n.value) &&
              this._ngOnDestroyHooks.add(n.value),
            n.value
          );
        }
        injectableDefInScope(t) {
          if (!t.providedIn) return !1;
          const n = k(t.providedIn);
          return "string" == typeof n
            ? "any" === n || this.scopes.has(n)
            : this.injectorDefTypes.has(n);
        }
        removeOnDestroy(t) {
          const n = this._onDestroyHooks.indexOf(t);
          -1 !== n && this._onDestroyHooks.splice(n, 1);
        }
      }
      function od(e) {
        const t = qs(e),
          n = null !== t ? t.factory : ar(e);
        if (null !== n) return n;
        if (e instanceof E) throw new v(204, !1);
        if (e instanceof Function)
          return (function nT(e) {
            const t = e.length;
            if (t > 0) throw (Eo(t, "?"), new v(204, !1));
            const n = (function VI(e) {
              return (e && (e[Ws] || e[Qp])) || null;
            })(e);
            return null !== n ? () => n.factory(e) : () => new e();
          })(e);
        throw new v(204, !1);
      }
      function li(e, t, n = !1) {
        return { factory: e, value: t, multi: n ? [] : void 0 };
      }
      function sd(e, t) {
        for (const n of e)
          Array.isArray(n) ? sd(n, t) : n && Gl(n) ? sd(n.ɵproviders, t) : t(n);
      }
      const Oa = new E("AppId", { providedIn: "root", factory: () => aT }),
        aT = "ng",
        wb = new E("Platform Initializer"),
        zn = new E("Platform ID", {
          providedIn: "platform",
          factory: () => "unknown",
        }),
        Oo = new E("AnimationModuleType"),
        ad = new E("CSP nonce", {
          providedIn: "root",
          factory: () =>
            (function ai() {
              if (void 0 !== Ku) return Ku;
              if (typeof document < "u") return document;
              throw new v(210, !1);
            })()
              .body?.querySelector("[ngCspNonce]")
              ?.getAttribute("ngCspNonce") || null,
        });
      let Eb = (e, t, n) => null;
      function md(e, t, n = !1) {
        return Eb(e, t, n);
      }
      class bT {}
      class Mb {}
      class vT {
        resolveComponentFactory(t) {
          throw (function yT(e) {
            const t = Error(`No component factory found for ${Ce(e)}.`);
            return (t.ngComponent = e), t;
          })(t);
        }
      }
      let Ba = (() => {
        class e {
          static {
            this.NULL = new vT();
          }
        }
        return e;
      })();
      function _T() {
        return fi(ke(), _());
      }
      function fi(e, t) {
        return new gt(it(e, t));
      }
      let gt = (() => {
        class e {
          constructor(n) {
            this.nativeElement = n;
          }
          static {
            this.__NG_ELEMENT_ID__ = _T;
          }
        }
        return e;
      })();
      class Fo {}
      let Va = (() => {
          class e {
            constructor() {
              this.destroyNode = null;
            }
            static {
              this.__NG_ELEMENT_ID__ = () =>
                (function wT() {
                  const e = _(),
                    n = ft(ke().index, e);
                  return (rt(n) ? n : e)[j];
                })();
            }
          }
          return e;
        })(),
        ET = (() => {
          class e {
            static {
              this.ɵprov = S({
                token: e,
                providedIn: "root",
                factory: () => null,
              });
            }
          }
          return e;
        })();
      class hi {
        constructor(t) {
          (this.full = t),
            (this.major = t.split(".")[0]),
            (this.minor = t.split(".")[1]),
            (this.patch = t.split(".").slice(2).join("."));
        }
      }
      const CT = new hi("16.2.12"),
        yd = {};
      function Nb(e, t = null, n = null, r) {
        const i = Rb(e, t, n, r);
        return i.resolveInjectorInitializers(), i;
      }
      function Rb(e, t = null, n = null, r, i = new Set()) {
        const o = [n || Z, Xx(e)];
        return (
          (r = r || ("object" == typeof e ? void 0 : Ce(e))),
          new ci(o, t || Ra(), r || null, i)
        );
      }
      let bt = (() => {
        class e {
          static {
            this.THROW_IF_NOT_FOUND = ro;
          }
          static {
            this.NULL = new Ju();
          }
          static create(n, r) {
            if (Array.isArray(n)) return Nb({ name: "" }, r, n, "");
            {
              const i = n.name ?? "";
              return Nb({ name: i }, n.parent, n.providers, i);
            }
          }
          static {
            this.ɵprov = S({
              token: e,
              providedIn: "any",
              factory: () => D(mb),
            });
          }
          static {
            this.__NG_ELEMENT_ID__ = -1;
          }
        }
        return e;
      })();
      function _d(e) {
        return e.ngOriginalError;
      }
      class xt {
        constructor() {
          this._console = console;
        }
        handleError(t) {
          const n = this._findOriginalError(t);
          this._console.error("ERROR", t),
            n && this._console.error("ORIGINAL ERROR", n);
        }
        _findOriginalError(t) {
          let n = t && _d(t);
          for (; n && _d(n); ) n = _d(n);
          return n || null;
        }
      }
      function Dd(e) {
        return (t) => {
          setTimeout(e, void 0, t);
        };
      }
      const Ye = class RT extends Te {
        constructor(t = !1) {
          super(), (this.__isAsync = t);
        }
        emit(t) {
          super.next(t);
        }
        subscribe(t, n, r) {
          let i = t,
            o = n || (() => null),
            s = r;
          if (t && "object" == typeof t) {
            const c = t;
            (i = c.next?.bind(c)),
              (o = c.error?.bind(c)),
              (s = c.complete?.bind(c));
          }
          this.__isAsync && ((o = Dd(o)), i && (i = Dd(i)), s && (s = Dd(s)));
          const a = super.subscribe({ next: i, error: o, complete: s });
          return t instanceof je && t.add(a), a;
        }
      };
      function Pb(...e) {}
      class W {
        constructor({
          enableLongStackTrace: t = !1,
          shouldCoalesceEventChangeDetection: n = !1,
          shouldCoalesceRunChangeDetection: r = !1,
        }) {
          if (
            ((this.hasPendingMacrotasks = !1),
            (this.hasPendingMicrotasks = !1),
            (this.isStable = !0),
            (this.onUnstable = new Ye(!1)),
            (this.onMicrotaskEmpty = new Ye(!1)),
            (this.onStable = new Ye(!1)),
            (this.onError = new Ye(!1)),
            typeof Zone > "u")
          )
            throw new v(908, !1);
          Zone.assertZonePatched();
          const i = this;
          (i._nesting = 0),
            (i._outer = i._inner = Zone.current),
            Zone.TaskTrackingZoneSpec &&
              (i._inner = i._inner.fork(new Zone.TaskTrackingZoneSpec())),
            t &&
              Zone.longStackTraceZoneSpec &&
              (i._inner = i._inner.fork(Zone.longStackTraceZoneSpec)),
            (i.shouldCoalesceEventChangeDetection = !r && n),
            (i.shouldCoalesceRunChangeDetection = r),
            (i.lastRequestAnimationFrameId = -1),
            (i.nativeRequestAnimationFrame = (function OT() {
              const e = "function" == typeof oe.requestAnimationFrame;
              let t = oe[e ? "requestAnimationFrame" : "setTimeout"],
                n = oe[e ? "cancelAnimationFrame" : "clearTimeout"];
              if (typeof Zone < "u" && t && n) {
                const r = t[Zone.__symbol__("OriginalDelegate")];
                r && (t = r);
                const i = n[Zone.__symbol__("OriginalDelegate")];
                i && (n = i);
              }
              return {
                nativeRequestAnimationFrame: t,
                nativeCancelAnimationFrame: n,
              };
            })().nativeRequestAnimationFrame),
            (function FT(e) {
              const t = () => {
                !(function kT(e) {
                  e.isCheckStableRunning ||
                    -1 !== e.lastRequestAnimationFrameId ||
                    ((e.lastRequestAnimationFrameId =
                      e.nativeRequestAnimationFrame.call(oe, () => {
                        e.fakeTopEventTask ||
                          (e.fakeTopEventTask = Zone.root.scheduleEventTask(
                            "fakeTopEventTask",
                            () => {
                              (e.lastRequestAnimationFrameId = -1),
                                Ed(e),
                                (e.isCheckStableRunning = !0),
                                wd(e),
                                (e.isCheckStableRunning = !1);
                            },
                            void 0,
                            () => {},
                            () => {},
                          )),
                          e.fakeTopEventTask.invoke();
                      })),
                    Ed(e));
                })(e);
              };
              e._inner = e._inner.fork({
                name: "angular",
                properties: { isAngularZone: !0 },
                onInvokeTask: (n, r, i, o, s, a) => {
                  if (
                    (function jT(e) {
                      return (
                        !(!Array.isArray(e) || 1 !== e.length) &&
                        !0 === e[0].data?.__ignore_ng_zone__
                      );
                    })(a)
                  )
                    return n.invokeTask(i, o, s, a);
                  try {
                    return kb(e), n.invokeTask(i, o, s, a);
                  } finally {
                    ((e.shouldCoalesceEventChangeDetection &&
                      "eventTask" === o.type) ||
                      e.shouldCoalesceRunChangeDetection) &&
                      t(),
                      Fb(e);
                  }
                },
                onInvoke: (n, r, i, o, s, a, c) => {
                  try {
                    return kb(e), n.invoke(i, o, s, a, c);
                  } finally {
                    e.shouldCoalesceRunChangeDetection && t(), Fb(e);
                  }
                },
                onHasTask: (n, r, i, o) => {
                  n.hasTask(i, o),
                    r === i &&
                      ("microTask" == o.change
                        ? ((e._hasPendingMicrotasks = o.microTask),
                          Ed(e),
                          wd(e))
                        : "macroTask" == o.change &&
                          (e.hasPendingMacrotasks = o.macroTask));
                },
                onHandleError: (n, r, i, o) => (
                  n.handleError(i, o),
                  e.runOutsideAngular(() => e.onError.emit(o)),
                  !1
                ),
              });
            })(i);
        }
        static isInAngularZone() {
          return typeof Zone < "u" && !0 === Zone.current.get("isAngularZone");
        }
        static assertInAngularZone() {
          if (!W.isInAngularZone()) throw new v(909, !1);
        }
        static assertNotInAngularZone() {
          if (W.isInAngularZone()) throw new v(909, !1);
        }
        run(t, n, r) {
          return this._inner.run(t, n, r);
        }
        runTask(t, n, r, i) {
          const o = this._inner,
            s = o.scheduleEventTask("NgZoneEvent: " + i, t, PT, Pb, Pb);
          try {
            return o.runTask(s, n, r);
          } finally {
            o.cancelTask(s);
          }
        }
        runGuarded(t, n, r) {
          return this._inner.runGuarded(t, n, r);
        }
        runOutsideAngular(t) {
          return this._outer.run(t);
        }
      }
      const PT = {};
      function wd(e) {
        if (0 == e._nesting && !e.hasPendingMicrotasks && !e.isStable)
          try {
            e._nesting++, e.onMicrotaskEmpty.emit(null);
          } finally {
            if ((e._nesting--, !e.hasPendingMicrotasks))
              try {
                e.runOutsideAngular(() => e.onStable.emit(null));
              } finally {
                e.isStable = !0;
              }
          }
      }
      function Ed(e) {
        e.hasPendingMicrotasks = !!(
          e._hasPendingMicrotasks ||
          ((e.shouldCoalesceEventChangeDetection ||
            e.shouldCoalesceRunChangeDetection) &&
            -1 !== e.lastRequestAnimationFrameId)
        );
      }
      function kb(e) {
        e._nesting++,
          e.isStable && ((e.isStable = !1), e.onUnstable.emit(null));
      }
      function Fb(e) {
        e._nesting--, wd(e);
      }
      class LT {
        constructor() {
          (this.hasPendingMicrotasks = !1),
            (this.hasPendingMacrotasks = !1),
            (this.isStable = !0),
            (this.onUnstable = new Ye()),
            (this.onMicrotaskEmpty = new Ye()),
            (this.onStable = new Ye()),
            (this.onError = new Ye());
        }
        run(t, n, r) {
          return t.apply(n, r);
        }
        runGuarded(t, n, r) {
          return t.apply(n, r);
        }
        runOutsideAngular(t) {
          return t();
        }
        runTask(t, n, r, i) {
          return t.apply(n, r);
        }
      }
      const Lb = new E("", { providedIn: "root", factory: jb });
      function jb() {
        const e = C(W);
        let t = !0;
        return (function NI(...e) {
          const t = no(e),
            n = (function CI(e, t) {
              return "number" == typeof Vl(e) ? e.pop() : t;
            })(e, 1 / 0),
            r = e;
          return r.length ? (1 === r.length ? ct(r[0]) : Lr(n)(Se(r, t))) : Zt;
        })(
          new pe((i) => {
            (t =
              e.isStable && !e.hasPendingMacrotasks && !e.hasPendingMicrotasks),
              e.runOutsideAngular(() => {
                i.next(t), i.complete();
              });
          }),
          new pe((i) => {
            let o;
            e.runOutsideAngular(() => {
              o = e.onStable.subscribe(() => {
                W.assertNotInAngularZone(),
                  queueMicrotask(() => {
                    !t &&
                      !e.hasPendingMacrotasks &&
                      !e.hasPendingMicrotasks &&
                      ((t = !0), i.next(!0));
                  });
              });
            });
            const s = e.onUnstable.subscribe(() => {
              W.assertInAngularZone(),
                t &&
                  ((t = !1),
                  e.runOutsideAngular(() => {
                    i.next(!1);
                  }));
            });
            return () => {
              o.unsubscribe(), s.unsubscribe();
            };
          }).pipe($l()),
        );
      }
      function wn(e) {
        return e instanceof Function ? e() : e;
      }
      let Cd = (() => {
        class e {
          constructor() {
            (this.renderDepth = 0), (this.handler = null);
          }
          begin() {
            this.handler?.validateBegin(), this.renderDepth++;
          }
          end() {
            this.renderDepth--,
              0 === this.renderDepth && this.handler?.execute();
          }
          ngOnDestroy() {
            this.handler?.destroy(), (this.handler = null);
          }
          static {
            this.ɵprov = S({
              token: e,
              providedIn: "root",
              factory: () => new e(),
            });
          }
        }
        return e;
      })();
      function Lo(e) {
        for (; e; ) {
          e[V] |= 64;
          const t = So(e);
          if (au(e) && !t) return e;
          e = t;
        }
        return null;
      }
      const Hb = new E("", { providedIn: "root", factory: () => !1 });
      let Ha = null;
      function Wb(e, t) {
        return e[t] ?? Qb();
      }
      function Kb(e, t) {
        const n = Qb();
        n.producerNode?.length && ((e[t] = Ha), (n.lView = e), (Ha = Zb()));
      }
      const KT = {
        ..._m,
        consumerIsAlwaysLive: !0,
        consumerMarkedDirty: (e) => {
          Lo(e.lView);
        },
        lView: null,
      };
      function Zb() {
        return Object.create(KT);
      }
      function Qb() {
        return (Ha ??= Zb()), Ha;
      }
      const B = {};
      function gi(e) {
        Yb(G(), _(), Ze() + e, !1);
      }
      function Yb(e, t, n, r) {
        if (!r)
          if (3 == (3 & t[V])) {
            const o = e.preOrderCheckHooks;
            null !== o && sa(t, o, n);
          } else {
            const o = e.preOrderHooks;
            null !== o && aa(t, o, 0, n);
          }
        lr(n);
      }
      function x(e, t = H.Default) {
        const n = _();
        return null === n ? D(e, t) : dg(ke(), n, k(e), t);
      }
      function Id() {
        throw new Error("invalid");
      }
      function za(e, t, n, r, i, o, s, a, c, l, u) {
        const d = t.blueprint.slice();
        return (
          (d[me] = i),
          (d[V] = 140 | r),
          (null !== l || (e && 2048 & e[V])) && (d[V] |= 2048),
          Vm(d),
          (d[de] = d[Ur] = e),
          (d[ye] = n),
          (d[$r] = s || (e && e[$r])),
          (d[j] = a || (e && e[j])),
          (d[jn] = c || (e && e[jn]) || null),
          (d[Ve] = o),
          (d[uo] = (function QS() {
            return ZS++;
          })()),
          (d[yn] = u),
          (d[gm] = l),
          (d[ve] = 2 == t.type ? e[ve] : d),
          d
        );
      }
      function bi(e, t, n, r, i) {
        let o = e.data[t];
        if (null === o)
          (o = (function Md(e, t, n, r, i) {
            const o = Gm(),
              s = mu(),
              c = (e.data[t] = (function nA(e, t, n, r, i, o) {
                let s = t ? t.injectorIndex : -1,
                  a = 0;
                return (
                  Wr() && (a |= 128),
                  {
                    type: n,
                    index: r,
                    insertBeforeIndex: null,
                    injectorIndex: s,
                    directiveStart: -1,
                    directiveEnd: -1,
                    directiveStylingLast: -1,
                    componentOffset: -1,
                    propertyBindings: null,
                    flags: a,
                    providerIndexes: 0,
                    value: i,
                    attrs: o,
                    mergedAttrs: null,
                    localNames: null,
                    initialInputs: void 0,
                    inputs: null,
                    outputs: null,
                    tView: null,
                    next: null,
                    prev: null,
                    projectionNext: null,
                    child: null,
                    parent: t,
                    projection: null,
                    styles: null,
                    stylesWithoutHost: null,
                    residualStyles: void 0,
                    classes: null,
                    classesWithoutHost: null,
                    residualClasses: void 0,
                    classBindings: 0,
                    styleBindings: 0,
                  }
                );
              })(0, s ? o : o && o.parent, n, t, r, i));
            return (
              null === e.firstChild && (e.firstChild = c),
              null !== o &&
                (s
                  ? null == o.child && null !== c.parent && (o.child = c)
                  : null === o.next && ((o.next = c), (c.prev = o))),
              c
            );
          })(e, t, n, r, i)),
            (function ZM() {
              return P.lFrame.inI18n;
            })() && (o.flags |= 32);
        else if (64 & o.type) {
          (o.type = n), (o.value = r), (o.attrs = i);
          const s = (function go() {
            const e = P.lFrame,
              t = e.currentTNode;
            return e.isParent ? t : t.parent;
          })();
          o.injectorIndex = null === s ? -1 : s.injectorIndex;
        }
        return en(o, !0), o;
      }
      function jo(e, t, n, r) {
        if (0 === n) return -1;
        const i = t.length;
        for (let o = 0; o < n; o++)
          t.push(r), e.blueprint.push(r), e.data.push(null);
        return i;
      }
      function Xb(e, t, n, r, i) {
        const o = Wb(t, fo),
          s = Ze(),
          a = 2 & r;
        try {
          lr(-1), a && t.length > z && Yb(e, t, z, !1), Jt(a ? 2 : 0, i);
          const l = a ? o : null,
            u = lu(l);
          try {
            null !== l && (l.dirty = !1), n(r, i);
          } finally {
            uu(l, u);
          }
        } finally {
          a && null === t[fo] && Kb(t, fo), lr(s), Jt(a ? 3 : 1, i);
        }
      }
      function Sd(e, t, n) {
        if (su(t)) {
          const r = Mt(null);
          try {
            const o = t.directiveEnd;
            for (let s = t.directiveStart; s < o; s++) {
              const a = e.data[s];
              a.contentQueries && a.contentQueries(1, n[s], s);
            }
          } finally {
            Mt(r);
          }
        }
      }
      function xd(e, t, n) {
        qm() &&
          ((function lA(e, t, n, r) {
            const i = n.directiveStart,
              o = n.directiveEnd;
            sr(n) &&
              (function gA(e, t, n) {
                const r = it(t, e),
                  i = Jb(n);
                let s = 16;
                n.signals ? (s = 4096) : n.onPush && (s = 64);
                const a = qa(
                  e,
                  za(
                    e,
                    i,
                    null,
                    s,
                    r,
                    t,
                    null,
                    e[$r].rendererFactory.createRenderer(r, n),
                    null,
                    null,
                    null,
                  ),
                );
                e[t.index] = a;
              })(t, n, e.data[i + n.componentOffset]),
              e.firstCreatePass || la(n, t),
              $e(r, t);
            const s = n.initialInputs;
            for (let a = i; a < o; a++) {
              const c = e.data[a],
                l = ur(t, e, a, n);
              $e(l, t),
                null !== s && bA(0, a - i, l, c, 0, s),
                Bt(c) && (ft(n.index, t)[ye] = ur(t, e, a, n));
            }
          })(e, t, n, it(n, t)),
          64 == (64 & n.flags) && iy(e, t, n));
      }
      function Td(e, t, n = it) {
        const r = t.localNames;
        if (null !== r) {
          let i = t.index + 1;
          for (let o = 0; o < r.length; o += 2) {
            const s = r[o + 1],
              a = -1 === s ? n(t, e) : e[s];
            e[i++] = a;
          }
        }
      }
      function Jb(e) {
        const t = e.tView;
        return null === t || t.incompleteFirstPass
          ? (e.tView = Ad(
              1,
              null,
              e.template,
              e.decls,
              e.vars,
              e.directiveDefs,
              e.pipeDefs,
              e.viewQuery,
              e.schemas,
              e.consts,
              e.id,
            ))
          : t;
      }
      function Ad(e, t, n, r, i, o, s, a, c, l, u) {
        const d = z + r,
          f = d + i,
          h = (function QT(e, t) {
            const n = [];
            for (let r = 0; r < t; r++) n.push(r < e ? null : B);
            return n;
          })(d, f),
          p = "function" == typeof l ? l() : l;
        return (h[I] = {
          type: e,
          blueprint: h,
          template: n,
          queries: null,
          viewQuery: a,
          declTNode: t,
          data: h.slice().fill(null, d),
          bindingStartIndex: d,
          expandoStartIndex: f,
          hostBindingOpCodes: null,
          firstCreatePass: !0,
          firstUpdatePass: !0,
          staticViewQueries: !1,
          staticContentQueries: !1,
          preOrderHooks: null,
          preOrderCheckHooks: null,
          contentHooks: null,
          contentCheckHooks: null,
          viewHooks: null,
          viewCheckHooks: null,
          destroyHooks: null,
          cleanup: null,
          contentQueries: null,
          components: null,
          directiveRegistry: "function" == typeof o ? o() : o,
          pipeRegistry: "function" == typeof s ? s() : s,
          firstChild: null,
          schemas: c,
          consts: p,
          incompleteFirstPass: !1,
          ssrId: u,
        });
      }
      let ey = (e) => null;
      function ty(e, t, n, r) {
        for (let i in e)
          if (e.hasOwnProperty(i)) {
            n = null === n ? {} : n;
            const o = e[i];
            null === r
              ? ny(n, t, i, o)
              : r.hasOwnProperty(i) && ny(n, t, r[i], o);
          }
        return n;
      }
      function ny(e, t, n, r) {
        e.hasOwnProperty(n) ? e[n].push(t, r) : (e[n] = [t, r]);
      }
      function Nd(e, t, n, r) {
        if (qm()) {
          const i = null === r ? null : { "": -1 },
            o = (function dA(e, t) {
              const n = e.directiveRegistry;
              let r = null,
                i = null;
              if (n)
                for (let o = 0; o < n.length; o++) {
                  const s = n[o];
                  if (um(t, s.selectors, !1))
                    if ((r || (r = []), Bt(s)))
                      if (null !== s.findHostDirectiveDefs) {
                        const a = [];
                        (i = i || new Map()),
                          s.findHostDirectiveDefs(s, a, i),
                          r.unshift(...a, s),
                          Rd(e, t, a.length);
                      } else r.unshift(s), Rd(e, t, 0);
                    else
                      (i = i || new Map()),
                        s.findHostDirectiveDefs?.(s, r, i),
                        r.push(s);
                }
              return null === r ? null : [r, i];
            })(e, n);
          let s, a;
          null === o ? (s = a = null) : ([s, a] = o),
            null !== s && ry(e, t, n, s, i, a),
            i &&
              (function fA(e, t, n) {
                if (t) {
                  const r = (e.localNames = []);
                  for (let i = 0; i < t.length; i += 2) {
                    const o = n[t[i + 1]];
                    if (null == o) throw new v(-301, !1);
                    r.push(t[i], o);
                  }
                }
              })(n, r, i);
        }
        n.mergedAttrs = so(n.mergedAttrs, n.attrs);
      }
      function ry(e, t, n, r, i, o) {
        for (let l = 0; l < r.length; l++) Su(la(n, t), e, r[l].type);
        !(function pA(e, t, n) {
          (e.flags |= 1),
            (e.directiveStart = t),
            (e.directiveEnd = t + n),
            (e.providerIndexes = t);
        })(n, e.data.length, r.length);
        for (let l = 0; l < r.length; l++) {
          const u = r[l];
          u.providersResolver && u.providersResolver(u);
        }
        let s = !1,
          a = !1,
          c = jo(e, t, r.length, null);
        for (let l = 0; l < r.length; l++) {
          const u = r[l];
          (n.mergedAttrs = so(n.mergedAttrs, u.hostAttrs)),
            mA(e, n, t, c, u),
            hA(c, u, i),
            null !== u.contentQueries && (n.flags |= 4),
            (null !== u.hostBindings ||
              null !== u.hostAttrs ||
              0 !== u.hostVars) &&
              (n.flags |= 64);
          const d = u.type.prototype;
          !s &&
            (d.ngOnChanges || d.ngOnInit || d.ngDoCheck) &&
            ((e.preOrderHooks ??= []).push(n.index), (s = !0)),
            !a &&
              (d.ngOnChanges || d.ngDoCheck) &&
              ((e.preOrderCheckHooks ??= []).push(n.index), (a = !0)),
            c++;
        }
        !(function rA(e, t, n) {
          const i = t.directiveEnd,
            o = e.data,
            s = t.attrs,
            a = [];
          let c = null,
            l = null;
          for (let u = t.directiveStart; u < i; u++) {
            const d = o[u],
              f = n ? n.get(d) : null,
              p = f ? f.outputs : null;
            (c = ty(d.inputs, u, c, f ? f.inputs : null)),
              (l = ty(d.outputs, u, l, p));
            const m = null === c || null === s || lm(t) ? null : yA(c, u, s);
            a.push(m);
          }
          null !== c &&
            (c.hasOwnProperty("class") && (t.flags |= 8),
            c.hasOwnProperty("style") && (t.flags |= 16)),
            (t.initialInputs = a),
            (t.inputs = c),
            (t.outputs = l);
        })(e, n, o);
      }
      function iy(e, t, n) {
        const r = n.directiveStart,
          i = n.directiveEnd,
          o = n.index,
          s = (function YM() {
            return P.lFrame.currentDirectiveIndex;
          })();
        try {
          lr(o);
          for (let a = r; a < i; a++) {
            const c = e.data[a],
              l = t[a];
            bu(a),
              (null !== c.hostBindings ||
                0 !== c.hostVars ||
                null !== c.hostAttrs) &&
                uA(c, l);
          }
        } finally {
          lr(-1), bu(s);
        }
      }
      function uA(e, t) {
        null !== e.hostBindings && e.hostBindings(1, t);
      }
      function Rd(e, t, n) {
        (t.componentOffset = n), (e.components ??= []).push(t.index);
      }
      function hA(e, t, n) {
        if (n) {
          if (t.exportAs)
            for (let r = 0; r < t.exportAs.length; r++) n[t.exportAs[r]] = e;
          Bt(t) && (n[""] = e);
        }
      }
      function mA(e, t, n, r, i) {
        e.data[r] = i;
        const o = i.factory || (i.factory = ar(i.type)),
          s = new bo(o, Bt(i), x);
        (e.blueprint[r] = s),
          (n[r] = s),
          (function aA(e, t, n, r, i) {
            const o = i.hostBindings;
            if (o) {
              let s = e.hostBindingOpCodes;
              null === s && (s = e.hostBindingOpCodes = []);
              const a = ~t.index;
              (function cA(e) {
                let t = e.length;
                for (; t > 0; ) {
                  const n = e[--t];
                  if ("number" == typeof n && n < 0) return n;
                }
                return 0;
              })(s) != a && s.push(a),
                s.push(n, r, o);
            }
          })(e, t, r, jo(e, n, i.hostVars, B), i);
      }
      function rn(e, t, n, r, i, o) {
        const s = it(e, t);
        !(function Od(e, t, n, r, i, o, s) {
          if (null == o) e.removeAttribute(t, i, n);
          else {
            const a = null == s ? L(o) : s(o, r || "", i);
            e.setAttribute(t, i, a, n);
          }
        })(t[j], s, o, e.value, n, r, i);
      }
      function bA(e, t, n, r, i, o) {
        const s = o[t];
        if (null !== s)
          for (let a = 0; a < s.length; ) oy(r, n, s[a++], s[a++], s[a++]);
      }
      function oy(e, t, n, r, i) {
        const o = Mt(null);
        try {
          const s = e.inputTransforms;
          null !== s && s.hasOwnProperty(r) && (i = s[r].call(t, i)),
            null !== e.setInput ? e.setInput(t, i, n, r) : (t[r] = i);
        } finally {
          Mt(o);
        }
      }
      function yA(e, t, n) {
        let r = null,
          i = 0;
        for (; i < n.length; ) {
          const o = n[i];
          if (0 !== o)
            if (5 !== o) {
              if ("number" == typeof o) break;
              if (e.hasOwnProperty(o)) {
                null === r && (r = []);
                const s = e[o];
                for (let a = 0; a < s.length; a += 2)
                  if (s[a] === t) {
                    r.push(o, s[a + 1], n[i + 1]);
                    break;
                  }
              }
              i += 2;
            } else i += 2;
          else i += 4;
        }
        return r;
      }
      function sy(e, t, n, r) {
        return [e, !0, !1, t, null, 0, r, n, null, null, null];
      }
      function ay(e, t) {
        const n = e.contentQueries;
        if (null !== n)
          for (let r = 0; r < n.length; r += 2) {
            const o = n[r + 1];
            if (-1 !== o) {
              const s = e.data[o];
              vu(n[r]), s.contentQueries(2, t[o], o);
            }
          }
      }
      function qa(e, t) {
        return e[co] ? (e[mm][jt] = t) : (e[co] = t), (e[mm] = t), t;
      }
      function Pd(e, t, n) {
        vu(0);
        const r = Mt(null);
        try {
          t(e, n);
        } finally {
          Mt(r);
        }
      }
      function dy(e, t) {
        const n = e[jn],
          r = n ? n.get(xt, null) : null;
        r && r.handleError(t);
      }
      function kd(e, t, n, r, i) {
        for (let o = 0; o < n.length; ) {
          const s = n[o++],
            a = n[o++];
          oy(e.data[s], t[s], r, a, i);
        }
      }
      function vA(e, t) {
        const n = ft(t, e),
          r = n[I];
        !(function _A(e, t) {
          for (let n = t.length; n < e.blueprint.length; n++)
            t.push(e.blueprint[n]);
        })(r, n);
        const i = n[me];
        null !== i && null === n[yn] && (n[yn] = md(i, n[jn])), Fd(r, n, n[ye]);
      }
      function Fd(e, t, n) {
        _u(t);
        try {
          const r = e.viewQuery;
          null !== r && Pd(1, r, n);
          const i = e.template;
          null !== i && Xb(e, t, i, 1, n),
            e.firstCreatePass && (e.firstCreatePass = !1),
            e.staticContentQueries && ay(e, t),
            e.staticViewQueries && Pd(2, e.viewQuery, n);
          const o = e.components;
          null !== o &&
            (function DA(e, t) {
              for (let n = 0; n < t.length; n++) vA(e, t[n]);
            })(t, o);
        } catch (r) {
          throw (
            (e.firstCreatePass &&
              ((e.incompleteFirstPass = !0), (e.firstCreatePass = !1)),
            r)
          );
        } finally {
          (t[V] &= -5), Du();
        }
      }
      let fy = (() => {
        class e {
          constructor() {
            (this.all = new Set()), (this.queue = new Map());
          }
          create(n, r, i) {
            const o = typeof Zone > "u" ? null : Zone.current,
              s = (function IM(e, t, n) {
                const r = Object.create(MM);
                n && (r.consumerAllowSignalWrites = !0),
                  (r.fn = e),
                  (r.schedule = t);
                const i = (s) => {
                  r.cleanupFn = s;
                };
                return (
                  (r.ref = {
                    notify: () => Cm(r),
                    run: () => {
                      if (((r.dirty = !1), r.hasRun && !Im(r))) return;
                      r.hasRun = !0;
                      const s = lu(r);
                      try {
                        r.cleanupFn(), (r.cleanupFn = Om), r.fn(i);
                      } finally {
                        uu(r, s);
                      }
                    },
                    cleanup: () => r.cleanupFn(),
                  }),
                  r.ref
                );
              })(
                n,
                (l) => {
                  this.all.has(l) && this.queue.set(l, o);
                },
                i,
              );
            let a;
            this.all.add(s), s.notify();
            const c = () => {
              s.cleanup(), a?.(), this.all.delete(s), this.queue.delete(s);
            };
            return (a = r?.onDestroy(c)), { destroy: c };
          }
          flush() {
            if (0 !== this.queue.size)
              for (const [n, r] of this.queue)
                this.queue.delete(n), r ? r.run(() => n.run()) : n.run();
          }
          get isQueueEmpty() {
            return 0 === this.queue.size;
          }
          static {
            this.ɵprov = S({
              token: e,
              providedIn: "root",
              factory: () => new e(),
            });
          }
        }
        return e;
      })();
      function Ga(e, t, n) {
        let r = n ? e.styles : null,
          i = n ? e.classes : null,
          o = 0;
        if (null !== t)
          for (let s = 0; s < t.length; s++) {
            const a = t[s];
            "number" == typeof a
              ? (o = a)
              : 1 == o
              ? (i = Hl(i, a))
              : 2 == o && (r = Hl(r, a + ": " + t[++s] + ";"));
          }
        n ? (e.styles = r) : (e.stylesWithoutHost = r),
          n ? (e.classes = i) : (e.classesWithoutHost = i);
      }
      function Bo(e, t, n, r, i = !1) {
        for (; null !== n; ) {
          const o = t[n.index];
          null !== o && r.push(se(o)), We(o) && hy(o, r);
          const s = n.type;
          if (8 & s) Bo(e, t, n.child, r);
          else if (32 & s) {
            const a = Bu(n, t);
            let c;
            for (; (c = a()); ) r.push(c);
          } else if (16 & s) {
            const a = Yg(t, n);
            if (Array.isArray(a)) r.push(...a);
            else {
              const c = So(t[ve]);
              Bo(c[I], c, a, r, !0);
            }
          }
          n = i ? n.projectionNext : n.next;
        }
        return r;
      }
      function hy(e, t) {
        for (let n = Oe; n < e.length; n++) {
          const r = e[n],
            i = r[I].firstChild;
          null !== i && Bo(r[I], r, i, t);
        }
        e[Xt] !== e[me] && t.push(e[Xt]);
      }
      function Wa(e, t, n, r = !0) {
        const i = t[$r],
          o = i.rendererFactory,
          s = i.afterRenderEventManager;
        o.begin?.(), s?.begin();
        try {
          py(e, t, e.template, n);
        } catch (c) {
          throw (r && dy(t, c), c);
        } finally {
          o.end?.(), i.effectManager?.flush(), s?.end();
        }
      }
      function py(e, t, n, r) {
        const i = t[V];
        if (256 != (256 & i)) {
          t[$r].effectManager?.flush(), _u(t);
          try {
            Vm(t),
              (function Km(e) {
                return (P.lFrame.bindingIndex = e);
              })(e.bindingStartIndex),
              null !== n && Xb(e, t, n, 2, r);
            const s = 3 == (3 & i);
            if (s) {
              const l = e.preOrderCheckHooks;
              null !== l && sa(t, l, null);
            } else {
              const l = e.preOrderHooks;
              null !== l && aa(t, l, 0, null), wu(t, 0);
            }
            if (
              ((function CA(e) {
                for (let t = Bg(e); null !== t; t = Vg(t)) {
                  if (!t[bm]) continue;
                  const n = t[zr];
                  for (let r = 0; r < n.length; r++) {
                    FM(n[r]);
                  }
                }
              })(t),
              my(t, 2),
              null !== e.contentQueries && ay(e, t),
              s)
            ) {
              const l = e.contentCheckHooks;
              null !== l && sa(t, l);
            } else {
              const l = e.contentHooks;
              null !== l && aa(t, l, 1), wu(t, 1);
            }
            !(function ZT(e, t) {
              const n = e.hostBindingOpCodes;
              if (null === n) return;
              const r = Wb(t, ho);
              try {
                for (let i = 0; i < n.length; i++) {
                  const o = n[i];
                  if (o < 0) lr(~o);
                  else {
                    const s = o,
                      a = n[++i],
                      c = n[++i];
                    QM(a, s), (r.dirty = !1);
                    const l = lu(r);
                    try {
                      c(2, t[s]);
                    } finally {
                      uu(r, l);
                    }
                  }
                }
              } finally {
                null === t[ho] && Kb(t, ho), lr(-1);
              }
            })(e, t);
            const a = e.components;
            null !== a && by(t, a, 0);
            const c = e.viewQuery;
            if ((null !== c && Pd(2, c, r), s)) {
              const l = e.viewCheckHooks;
              null !== l && sa(t, l);
            } else {
              const l = e.viewHooks;
              null !== l && aa(t, l, 2), wu(t, 2);
            }
            !0 === e.firstUpdatePass && (e.firstUpdatePass = !1),
              (t[V] &= -73),
              $m(t);
          } finally {
            Du();
          }
        }
      }
      function my(e, t) {
        for (let n = Bg(e); null !== n; n = Vg(n))
          for (let r = Oe; r < n.length; r++) gy(n[r], t);
      }
      function IA(e, t, n) {
        gy(ft(t, e), n);
      }
      function gy(e, t) {
        if (
          !(function PM(e) {
            return 128 == (128 & e[V]);
          })(e)
        )
          return;
        const n = e[I],
          r = e[V];
        if ((80 & r && 0 === t) || 1024 & r || 2 === t)
          py(n, e, n.template, e[ye]);
        else if (e[ao] > 0) {
          my(e, 1);
          const i = n.components;
          null !== i && by(e, i, 1);
        }
      }
      function by(e, t, n) {
        for (let r = 0; r < t.length; r++) IA(e, t[r], n);
      }
      class Vo {
        get rootNodes() {
          const t = this._lView,
            n = t[I];
          return Bo(n, t, n.firstChild, []);
        }
        constructor(t, n) {
          (this._lView = t),
            (this._cdRefInjectingView = n),
            (this._appRef = null),
            (this._attachedToViewContainer = !1);
        }
        get context() {
          return this._lView[ye];
        }
        set context(t) {
          this._lView[ye] = t;
        }
        get destroyed() {
          return 256 == (256 & this._lView[V]);
        }
        destroy() {
          if (this._appRef) this._appRef.detachView(this);
          else if (this._attachedToViewContainer) {
            const t = this._lView[de];
            if (We(t)) {
              const n = t[8],
                r = n ? n.indexOf(this) : -1;
              r > -1 && (wa(t, r), fa(n, r));
            }
            this._attachedToViewContainer = !1;
          }
          $u(this._lView[I], this._lView);
        }
        onDestroy(t) {
          !(function Hm(e, t) {
            if (256 == (256 & e[V])) throw new v(911, !1);
            null === e[Bn] && (e[Bn] = []), e[Bn].push(t);
          })(this._lView, t);
        }
        markForCheck() {
          Lo(this._cdRefInjectingView || this._lView);
        }
        detach() {
          this._lView[V] &= -129;
        }
        reattach() {
          this._lView[V] |= 128;
        }
        detectChanges() {
          Wa(this._lView[I], this._lView, this.context);
        }
        checkNoChanges() {}
        attachToViewContainerRef() {
          if (this._appRef) throw new v(902, !1);
          this._attachedToViewContainer = !0;
        }
        detachFromAppRef() {
          (this._appRef = null),
            (function ux(e, t) {
              To(e, t, t[j], 2, null, null);
            })(this._lView[I], this._lView);
        }
        attachToAppRef(t) {
          if (this._attachedToViewContainer) throw new v(902, !1);
          this._appRef = t;
        }
      }
      class MA extends Vo {
        constructor(t) {
          super(t), (this._view = t);
        }
        detectChanges() {
          const t = this._view;
          Wa(t[I], t, t[ye], !1);
        }
        checkNoChanges() {}
        get context() {
          return null;
        }
      }
      class yy extends Ba {
        constructor(t) {
          super(), (this.ngModule = t);
        }
        resolveComponentFactory(t) {
          const n = q(t);
          return new $o(n, this.ngModule);
        }
      }
      function vy(e) {
        const t = [];
        for (let n in e)
          e.hasOwnProperty(n) && t.push({ propName: e[n], templateName: n });
        return t;
      }
      class xA {
        constructor(t, n) {
          (this.injector = t), (this.parentInjector = n);
        }
        get(t, n, r) {
          r = Zs(r);
          const i = this.injector.get(t, yd, r);
          return i !== yd || n === yd ? i : this.parentInjector.get(t, n, r);
        }
      }
      class $o extends Mb {
        get inputs() {
          const t = this.componentDef,
            n = t.inputTransforms,
            r = vy(t.inputs);
          if (null !== n)
            for (const i of r)
              n.hasOwnProperty(i.propName) && (i.transform = n[i.propName]);
          return r;
        }
        get outputs() {
          return vy(this.componentDef.outputs);
        }
        constructor(t, n) {
          super(),
            (this.componentDef = t),
            (this.ngModule = n),
            (this.componentType = t.type),
            (this.selector = (function sM(e) {
              return e.map(oM).join(",");
            })(t.selectors)),
            (this.ngContentSelectors = t.ngContentSelectors
              ? t.ngContentSelectors
              : []),
            (this.isBoundToModule = !!n);
        }
        create(t, n, r, i) {
          let o = (i = i || this.ngModule) instanceof mt ? i : i?.injector;
          o &&
            null !== this.componentDef.getStandaloneInjector &&
            (o = this.componentDef.getStandaloneInjector(o) || o);
          const s = o ? new xA(t, o) : t,
            a = s.get(Fo, null);
          if (null === a) throw new v(407, !1);
          const d = {
              rendererFactory: a,
              sanitizer: s.get(ET, null),
              effectManager: s.get(fy, null),
              afterRenderEventManager: s.get(Cd, null),
            },
            f = a.createRenderer(null, this.componentDef),
            h = this.componentDef.selectors[0][0] || "div",
            p = r
              ? (function YT(e, t, n, r) {
                  const o = r.get(Hb, !1) || n === It.ShadowDom,
                    s = e.selectRootElement(t, o);
                  return (
                    (function XT(e) {
                      ey(e);
                    })(s),
                    s
                  );
                })(f, r, this.componentDef.encapsulation, s)
              : Da(
                  f,
                  h,
                  (function SA(e) {
                    const t = e.toLowerCase();
                    return "svg" === t ? "svg" : "math" === t ? "math" : null;
                  })(h),
                ),
            y = this.componentDef.signals
              ? 4608
              : this.componentDef.onPush
              ? 576
              : 528;
          let b = null;
          null !== p && (b = md(p, s, !0));
          const w = Ad(0, null, null, 1, 0, null, null, null, null, null, null),
            M = za(null, w, null, y, null, null, d, f, s, null, b);
          let F, te;
          _u(M);
          try {
            const ue = this.componentDef;
            let Le,
              wt = null;
            ue.findHostDirectiveDefs
              ? ((Le = []),
                (wt = new Map()),
                ue.findHostDirectiveDefs(ue, Le, wt),
                Le.push(ue))
              : (Le = [ue]);
            const Kt = (function AA(e, t) {
                const n = e[I],
                  r = z;
                return (e[r] = t), bi(n, r, 2, "#host", null);
              })(M, p),
              Sl = (function NA(e, t, n, r, i, o, s) {
                const a = i[I];
                !(function RA(e, t, n, r) {
                  for (const i of e)
                    t.mergedAttrs = so(t.mergedAttrs, i.hostAttrs);
                  null !== t.mergedAttrs &&
                    (Ga(t, t.mergedAttrs, !0), null !== n && tb(r, n, t));
                })(r, e, t, s);
                let c = null;
                null !== t && (c = md(t, i[jn]));
                const l = o.rendererFactory.createRenderer(t, n);
                let u = 16;
                n.signals ? (u = 4096) : n.onPush && (u = 64);
                const d = za(
                  i,
                  Jb(n),
                  null,
                  u,
                  i[e.index],
                  e,
                  o,
                  l,
                  null,
                  null,
                  c,
                );
                return (
                  a.firstCreatePass && Rd(a, e, r.length - 1),
                  qa(i, d),
                  (i[e.index] = d)
                );
              })(Kt, p, ue, Le, M, d, f);
            (te = Bm(w, z)),
              p &&
                (function PA(e, t, n, r) {
                  if (r) iu(e, n, ["ng-version", CT.full]);
                  else {
                    const { attrs: i, classes: o } = (function aM(e) {
                      const t = [],
                        n = [];
                      let r = 1,
                        i = 2;
                      for (; r < e.length; ) {
                        let o = e[r];
                        if ("string" == typeof o)
                          2 === i
                            ? "" !== o && t.push(o, e[++r])
                            : 8 === i && n.push(o);
                        else {
                          if (!Lt(i)) break;
                          i = o;
                        }
                        r++;
                      }
                      return { attrs: t, classes: n };
                    })(t.selectors[0]);
                    i && iu(e, n, i),
                      o && o.length > 0 && eb(e, n, o.join(" "));
                  }
                })(f, ue, p, r),
              void 0 !== n &&
                (function kA(e, t, n) {
                  const r = (e.projection = []);
                  for (let i = 0; i < t.length; i++) {
                    const o = n[i];
                    r.push(null != o ? Array.from(o) : null);
                  }
                })(te, this.ngContentSelectors, n),
              (F = (function OA(e, t, n, r, i, o) {
                const s = ke(),
                  a = i[I],
                  c = it(s, i);
                ry(a, i, s, n, null, r);
                for (let u = 0; u < n.length; u++)
                  $e(ur(i, a, s.directiveStart + u, s), i);
                iy(a, i, s), c && $e(c, i);
                const l = ur(i, a, s.directiveStart + s.componentOffset, s);
                if (((e[ye] = i[ye] = l), null !== o))
                  for (const u of o) u(l, t);
                return Sd(a, s, e), l;
              })(Sl, ue, Le, wt, M, [FA])),
              Fd(w, M, null);
          } finally {
            Du();
          }
          return new TA(this.componentType, F, fi(te, M), M, te);
        }
      }
      class TA extends bT {
        constructor(t, n, r, i, o) {
          super(),
            (this.location = r),
            (this._rootLView = i),
            (this._tNode = o),
            (this.previousInputValues = null),
            (this.instance = n),
            (this.hostView = this.changeDetectorRef = new MA(i)),
            (this.componentType = t);
        }
        setInput(t, n) {
          const r = this._tNode.inputs;
          let i;
          if (null !== r && (i = r[t])) {
            if (
              ((this.previousInputValues ??= new Map()),
              this.previousInputValues.has(t) &&
                Object.is(this.previousInputValues.get(t), n))
            )
              return;
            const o = this._rootLView;
            kd(o[I], o, i, t, n),
              this.previousInputValues.set(t, n),
              Lo(ft(this._tNode.index, o));
          }
        }
        get injector() {
          return new Qe(this._tNode, this._rootLView);
        }
        destroy() {
          this.hostView.destroy();
        }
        onDestroy(t) {
          this.hostView.onDestroy(t);
        }
      }
      function FA() {
        const e = ke();
        oa(_()[I], e);
      }
      function Uo(e) {
        let t = (function _y(e) {
            return Object.getPrototypeOf(e.prototype).constructor;
          })(e.type),
          n = !0;
        const r = [e];
        for (; t; ) {
          let i;
          if (Bt(e)) i = t.ɵcmp || t.ɵdir;
          else {
            if (t.ɵcmp) throw new v(903, !1);
            i = t.ɵdir;
          }
          if (i) {
            if (n) {
              r.push(i);
              const s = e;
              (s.inputs = Ka(e.inputs)),
                (s.inputTransforms = Ka(e.inputTransforms)),
                (s.declaredInputs = Ka(e.declaredInputs)),
                (s.outputs = Ka(e.outputs));
              const a = i.hostBindings;
              a && VA(e, a);
              const c = i.viewQuery,
                l = i.contentQueries;
              if (
                (c && jA(e, c),
                l && BA(e, l),
                Hs(e.inputs, i.inputs),
                Hs(e.declaredInputs, i.declaredInputs),
                Hs(e.outputs, i.outputs),
                null !== i.inputTransforms &&
                  (null === s.inputTransforms && (s.inputTransforms = {}),
                  Hs(s.inputTransforms, i.inputTransforms)),
                Bt(i) && i.data.animation)
              ) {
                const u = e.data;
                u.animation = (u.animation || []).concat(i.data.animation);
              }
            }
            const o = i.features;
            if (o)
              for (let s = 0; s < o.length; s++) {
                const a = o[s];
                a && a.ngInherit && a(e), a === Uo && (n = !1);
              }
          }
          t = Object.getPrototypeOf(t);
        }
        !(function LA(e) {
          let t = 0,
            n = null;
          for (let r = e.length - 1; r >= 0; r--) {
            const i = e[r];
            (i.hostVars = t += i.hostVars),
              (i.hostAttrs = so(i.hostAttrs, (n = so(n, i.hostAttrs))));
          }
        })(r);
      }
      function Ka(e) {
        return e === Qt ? {} : e === Z ? [] : e;
      }
      function jA(e, t) {
        const n = e.viewQuery;
        e.viewQuery = n
          ? (r, i) => {
              t(r, i), n(r, i);
            }
          : t;
      }
      function BA(e, t) {
        const n = e.contentQueries;
        e.contentQueries = n
          ? (r, i, o) => {
              t(r, i, o), n(r, i, o);
            }
          : t;
      }
      function VA(e, t) {
        const n = e.hostBindings;
        e.hostBindings = n
          ? (r, i) => {
              t(r, i), n(r, i);
            }
          : t;
      }
      function Za(e) {
        return (
          !!Ld(e) &&
          (Array.isArray(e) || (!(e instanceof Map) && Symbol.iterator in e))
        );
      }
      function Ld(e) {
        return null !== e && ("function" == typeof e || "object" == typeof e);
      }
      function Ue(e, t, n) {
        return !Object.is(e[t], n) && ((e[t] = n), !0);
      }
      function zo(e, t, n, r) {
        const i = _();
        return Ue(i, Kr(), t) && (G(), rn(fe(), i, e, t, n, r)), zo;
      }
      function ec(e, t, n, r, i, o, s, a) {
        const c = _(),
          l = G(),
          u = e + z,
          d = l.firstCreatePass
            ? (function dN(e, t, n, r, i, o, s, a, c) {
                const l = t.consts,
                  u = bi(t, e, 4, s || null, $n(l, a));
                Nd(t, n, u, $n(l, c)), oa(t, u);
                const d = (u.tView = Ad(
                  2,
                  u,
                  r,
                  i,
                  o,
                  t.directiveRegistry,
                  t.pipeRegistry,
                  null,
                  t.schemas,
                  l,
                  null,
                ));
                return (
                  null !== t.queries &&
                    (t.queries.template(t, u),
                    (d.queries = t.queries.embeddedTView(u))),
                  u
                );
              })(u, l, c, t, n, r, i, o, s)
            : l.data[u];
        en(d, !1);
        const f = Ly(l, c, d, e);
        ia() && Ca(l, c, f, d),
          $e(f, c),
          qa(c, (c[u] = sy(f, c, f, d))),
          ea(d) && xd(l, c, d),
          null != s && Td(c, d, a);
      }
      let Ly = function jy(e, t, n, r) {
        return Un(!0), t[j].createComment("");
      };
      function Si(e, t, n) {
        const r = _();
        return (
          Ue(r, Kr(), t) &&
            (function yt(e, t, n, r, i, o, s, a) {
              const c = it(t, n);
              let u,
                l = t.inputs;
              !a && null != l && (u = l[r])
                ? (kd(e, n, u, r, i),
                  sr(t) &&
                    (function oA(e, t) {
                      const n = ft(t, e);
                      16 & n[V] || (n[V] |= 64);
                    })(n, t.index))
                : 3 & t.type &&
                  ((r = (function iA(e) {
                    return "class" === e
                      ? "className"
                      : "for" === e
                      ? "htmlFor"
                      : "formaction" === e
                      ? "formAction"
                      : "innerHtml" === e
                      ? "innerHTML"
                      : "readonly" === e
                      ? "readOnly"
                      : "tabindex" === e
                      ? "tabIndex"
                      : e;
                  })(r)),
                  (i = null != s ? s(i, t.value || "", r) : i),
                  o.setProperty(c, r, i));
            })(G(), fe(), r, e, t, r[j], n, !1),
          Si
        );
      }
      function Hd(e, t, n, r, i) {
        const s = i ? "class" : "style";
        kd(e, n, t.inputs[s], s, r);
      }
      function He(e, t, n, r) {
        const i = _(),
          o = G(),
          s = z + e,
          a = i[j],
          c = o.firstCreatePass
            ? (function gN(e, t, n, r, i, o) {
                const s = t.consts,
                  c = bi(t, e, 2, r, $n(s, i));
                return (
                  Nd(t, n, c, $n(s, o)),
                  null !== c.attrs && Ga(c, c.attrs, !1),
                  null !== c.mergedAttrs && Ga(c, c.mergedAttrs, !0),
                  null !== t.queries && t.queries.elementStart(t, c),
                  c
                );
              })(s, o, i, t, n, r)
            : o.data[s],
          l = By(o, i, c, a, t, e);
        i[s] = l;
        const u = ea(c);
        return (
          en(c, !0),
          tb(a, l, c),
          32 != (32 & c.flags) && ia() && Ca(o, i, l, c),
          0 ===
            (function jM() {
              return P.lFrame.elementDepthCount;
            })() && $e(l, i),
          (function BM() {
            P.lFrame.elementDepthCount++;
          })(),
          u && (xd(o, i, c), Sd(o, c, i)),
          null !== r && Td(i, c),
          He
        );
      }
      function ze() {
        let e = ke();
        mu() ? gu() : ((e = e.parent), en(e, !1));
        const t = e;
        (function $M(e) {
          return P.skipHydrationRootTNode === e;
        })(t) &&
          (function qM() {
            P.skipHydrationRootTNode = null;
          })(),
          (function VM() {
            P.lFrame.elementDepthCount--;
          })();
        const n = G();
        return (
          n.firstCreatePass && (oa(n, e), su(e) && n.queries.elementEnd(e)),
          null != t.classesWithoutHost &&
            (function cS(e) {
              return 0 != (8 & e.flags);
            })(t) &&
            Hd(n, t, _(), t.classesWithoutHost, !0),
          null != t.stylesWithoutHost &&
            (function lS(e) {
              return 0 != (16 & e.flags);
            })(t) &&
            Hd(n, t, _(), t.stylesWithoutHost, !1),
          ze
        );
      }
      function gr(e, t, n, r) {
        return He(e, t, n, r), ze(), gr;
      }
      let By = (e, t, n, r, i, o) => (
        Un(!0),
        Da(
          r,
          i,
          (function ng() {
            return P.lFrame.currentNamespace;
          })(),
        )
      );
      function tc(e) {
        return !!e && "function" == typeof e.then;
      }
      function Uy(e) {
        return !!e && "function" == typeof e.subscribe;
      }
      function nc(e, t, n, r) {
        const i = _(),
          o = G(),
          s = ke();
        return (
          (function zy(e, t, n, r, i, o, s) {
            const a = ea(r),
              l =
                e.firstCreatePass &&
                (function ly(e) {
                  return e.cleanup || (e.cleanup = []);
                })(e),
              u = t[ye],
              d = (function cy(e) {
                return e[Vr] || (e[Vr] = []);
              })(t);
            let f = !0;
            if (3 & r.type || s) {
              const m = it(r, t),
                g = s ? s(m) : m,
                y = d.length,
                b = s ? (M) => s(se(M[r.index])) : r.index;
              let w = null;
              if (
                (!s &&
                  a &&
                  (w = (function EN(e, t, n, r) {
                    const i = e.cleanup;
                    if (null != i)
                      for (let o = 0; o < i.length - 1; o += 2) {
                        const s = i[o];
                        if (s === n && i[o + 1] === r) {
                          const a = t[Vr],
                            c = i[o + 2];
                          return a.length > c ? a[c] : null;
                        }
                        "string" == typeof s && (o += 2);
                      }
                    return null;
                  })(e, t, i, r.index)),
                null !== w)
              )
                ((w.__ngLastListenerFn__ || w).__ngNextListenerFn__ = o),
                  (w.__ngLastListenerFn__ = o),
                  (f = !1);
              else {
                o = Gy(r, t, u, o, !1);
                const M = n.listen(g, i, o);
                d.push(o, M), l && l.push(i, b, y, y + 1);
              }
            } else o = Gy(r, t, u, o, !1);
            const h = r.outputs;
            let p;
            if (f && null !== h && (p = h[i])) {
              const m = p.length;
              if (m)
                for (let g = 0; g < m; g += 2) {
                  const F = t[p[g]][p[g + 1]].subscribe(o),
                    te = d.length;
                  d.push(o, F), l && l.push(i, r.index, te, -(te + 1));
                }
            }
          })(o, i, i[j], s, e, t, r),
          nc
        );
      }
      function qy(e, t, n, r) {
        try {
          return Jt(6, t, n), !1 !== n(r);
        } catch (i) {
          return dy(e, i), !1;
        } finally {
          Jt(7, t, n);
        }
      }
      function Gy(e, t, n, r, i) {
        return function o(s) {
          if (s === Function) return r;
          Lo(e.componentOffset > -1 ? ft(e.index, t) : t);
          let c = qy(t, n, r, s),
            l = o.__ngNextListenerFn__;
          for (; l; ) (c = qy(t, n, l, s) && c), (l = l.__ngNextListenerFn__);
          return i && !1 === c && s.preventDefault(), c;
        };
      }
      function IN(e, t) {
        let n = null;
        const r = (function tM(e) {
          const t = e.attrs;
          if (null != t) {
            const n = t.indexOf(5);
            if (!(1 & n)) return t[n + 1];
          }
          return null;
        })(e);
        for (let i = 0; i < t.length; i++) {
          const o = t[i];
          if ("*" !== o) {
            if (null === r ? um(e, o, !0) : iM(r, o)) return i;
          } else n = i;
        }
        return n;
      }
      function xi(e) {
        const t = _()[ve][Ve];
        if (!t.projection) {
          const r = (t.projection = Eo(e ? e.length : 1, null)),
            i = r.slice();
          let o = t.child;
          for (; null !== o; ) {
            const s = e ? IN(o, e) : 0;
            null !== s &&
              (i[s] ? (i[s].projectionNext = o) : (r[s] = o), (i[s] = o)),
              (o = o.next);
          }
        }
      }
      function At(e, t = 0, n) {
        const r = _(),
          i = G(),
          o = bi(i, z + e, 16, null, n || null);
        null === o.projection && (o.projection = t),
          gu(),
          (!r[yn] || Wr()) &&
            32 != (32 & o.flags) &&
            (function yx(e, t, n) {
              Jg(t[j], 0, t, n, Hu(e, n, t), Wg(n.parent || t[Ve], n, t));
            })(i, r, o);
      }
      function rc(e, t) {
        return (e << 17) | (t << 2);
      }
      function qn(e) {
        return (e >> 17) & 32767;
      }
      function Wd(e) {
        return 2 | e;
      }
      function br(e) {
        return (131068 & e) >> 2;
      }
      function Kd(e, t) {
        return (-131069 & e) | (t << 2);
      }
      function Zd(e) {
        return 1 | e;
      }
      function nv(e, t, n, r, i) {
        const o = e[n + 1],
          s = null === t;
        let a = r ? qn(o) : br(o),
          c = !1;
        for (; 0 !== a && (!1 === c || s); ) {
          const u = e[a + 1];
          NN(e[a], t) && ((c = !0), (e[a + 1] = r ? Zd(u) : Wd(u))),
            (a = r ? qn(u) : br(u));
        }
        c && (e[n + 1] = r ? Wd(o) : Zd(o));
      }
      function NN(e, t) {
        return (
          null === e ||
          null == t ||
          (Array.isArray(e) ? e[1] : e) === t ||
          (!(!Array.isArray(e) || "string" != typeof t) && ni(e, t) >= 0)
        );
      }
      function Gn(e, t) {
        return (
          (function Vt(e, t, n, r) {
            const i = _(),
              o = G(),
              s = (function _n(e) {
                const t = P.lFrame,
                  n = t.bindingIndex;
                return (t.bindingIndex = t.bindingIndex + e), n;
              })(2);
            o.firstUpdatePass &&
              (function dv(e, t, n, r) {
                const i = e.data;
                if (null === i[n + 1]) {
                  const o = i[Ze()],
                    s = (function uv(e, t) {
                      return t >= e.expandoStartIndex;
                    })(e, n);
                  (function mv(e, t) {
                    return 0 != (e.flags & (t ? 8 : 16));
                  })(o, r) &&
                    null === t &&
                    !s &&
                    (t = !1),
                    (t = (function VN(e, t, n, r) {
                      const i = (function yu(e) {
                        const t = P.lFrame.currentDirectiveIndex;
                        return -1 === t ? null : e[t];
                      })(e);
                      let o = r ? t.residualClasses : t.residualStyles;
                      if (null === i)
                        0 === (r ? t.classBindings : t.styleBindings) &&
                          ((n = Ko((n = Qd(null, e, t, n, r)), t.attrs, r)),
                          (o = null));
                      else {
                        const s = t.directiveStylingLast;
                        if (-1 === s || e[s] !== i)
                          if (((n = Qd(i, e, t, n, r)), null === o)) {
                            let c = (function $N(e, t, n) {
                              const r = n ? t.classBindings : t.styleBindings;
                              if (0 !== br(r)) return e[qn(r)];
                            })(e, t, r);
                            void 0 !== c &&
                              Array.isArray(c) &&
                              ((c = Qd(null, e, t, c[1], r)),
                              (c = Ko(c, t.attrs, r)),
                              (function UN(e, t, n, r) {
                                e[qn(n ? t.classBindings : t.styleBindings)] =
                                  r;
                              })(e, t, r, c));
                          } else
                            o = (function HN(e, t, n) {
                              let r;
                              const i = t.directiveEnd;
                              for (
                                let o = 1 + t.directiveStylingLast;
                                o < i;
                                o++
                              )
                                r = Ko(r, e[o].hostAttrs, n);
                              return Ko(r, t.attrs, n);
                            })(e, t, r);
                      }
                      return (
                        void 0 !== o &&
                          (r
                            ? (t.residualClasses = o)
                            : (t.residualStyles = o)),
                        n
                      );
                    })(i, o, t, r)),
                    (function TN(e, t, n, r, i, o) {
                      let s = o ? t.classBindings : t.styleBindings,
                        a = qn(s),
                        c = br(s);
                      e[r] = n;
                      let u,
                        l = !1;
                      if (
                        (Array.isArray(n)
                          ? ((u = n[1]),
                            (null === u || ni(n, u) > 0) && (l = !0))
                          : (u = n),
                        i)
                      )
                        if (0 !== c) {
                          const f = qn(e[a + 1]);
                          (e[r + 1] = rc(f, a)),
                            0 !== f && (e[f + 1] = Kd(e[f + 1], r)),
                            (e[a + 1] = (function SN(e, t) {
                              return (131071 & e) | (t << 17);
                            })(e[a + 1], r));
                        } else
                          (e[r + 1] = rc(a, 0)),
                            0 !== a && (e[a + 1] = Kd(e[a + 1], r)),
                            (a = r);
                      else
                        (e[r + 1] = rc(c, 0)),
                          0 === a ? (a = r) : (e[c + 1] = Kd(e[c + 1], r)),
                          (c = r);
                      l && (e[r + 1] = Wd(e[r + 1])),
                        nv(e, u, r, !0),
                        nv(e, u, r, !1),
                        (function AN(e, t, n, r, i) {
                          const o = i ? e.residualClasses : e.residualStyles;
                          null != o &&
                            "string" == typeof t &&
                            ni(o, t) >= 0 &&
                            (n[r + 1] = Zd(n[r + 1]));
                        })(t, u, e, r, o),
                        (s = rc(a, c)),
                        o ? (t.classBindings = s) : (t.styleBindings = s);
                    })(i, o, t, n, s, r);
                }
              })(o, e, s, r),
              t !== B &&
                Ue(i, s, t) &&
                (function hv(e, t, n, r, i, o, s, a) {
                  if (!(3 & t.type)) return;
                  const c = e.data,
                    l = c[a + 1],
                    u = (function xN(e) {
                      return 1 == (1 & e);
                    })(l)
                      ? pv(c, t, n, i, br(l), s)
                      : void 0;
                  ic(u) ||
                    (ic(o) ||
                      ((function MN(e) {
                        return 2 == (2 & e);
                      })(l) &&
                        (o = pv(c, null, n, i, a, s))),
                    (function _x(e, t, n, r, i) {
                      if (t) i ? e.addClass(n, r) : e.removeClass(n, r);
                      else {
                        let o = -1 === r.indexOf("-") ? void 0 : Hn.DashCase;
                        null == i
                          ? e.removeStyle(n, r, o)
                          : ("string" == typeof i &&
                              i.endsWith("!important") &&
                              ((i = i.slice(0, -10)), (o |= Hn.Important)),
                            e.setStyle(n, r, i, o));
                      }
                    })(r, s, ra(Ze(), n), i, o));
                })(
                  o,
                  o.data[Ze()],
                  i,
                  i[j],
                  e,
                  (i[s + 1] = (function WN(e, t) {
                    return (
                      null == e ||
                        "" === e ||
                        ("string" == typeof t
                          ? (e += t)
                          : "object" == typeof e && (e = Ce(pt(e)))),
                      e
                    );
                  })(t, n)),
                  r,
                  s,
                );
          })(e, t, null, !0),
          Gn
        );
      }
      function Qd(e, t, n, r, i) {
        let o = null;
        const s = n.directiveEnd;
        let a = n.directiveStylingLast;
        for (
          -1 === a ? (a = n.directiveStart) : a++;
          a < s && ((o = t[a]), (r = Ko(r, o.hostAttrs, i)), o !== e);

        )
          a++;
        return null !== e && (n.directiveStylingLast = a), r;
      }
      function Ko(e, t, n) {
        const r = n ? 1 : 2;
        let i = -1;
        if (null !== t)
          for (let o = 0; o < t.length; o++) {
            const s = t[o];
            "number" == typeof s
              ? (i = s)
              : i === r &&
                (Array.isArray(e) || (e = void 0 === e ? [] : ["", e]),
                ht(e, s, !!n || t[++o]));
          }
        return void 0 === e ? null : e;
      }
      function pv(e, t, n, r, i, o) {
        const s = null === t;
        let a;
        for (; i > 0; ) {
          const c = e[i],
            l = Array.isArray(c),
            u = l ? c[1] : c,
            d = null === u;
          let f = n[i + 1];
          f === B && (f = d ? Z : void 0);
          let h = d ? Au(f, r) : u === r ? f : void 0;
          if ((l && !ic(h) && (h = Au(c, r)), ic(h) && ((a = h), s))) return a;
          const p = e[i + 1];
          i = s ? qn(p) : br(p);
        }
        if (null !== t) {
          let c = o ? t.residualClasses : t.residualStyles;
          null != c && (a = Au(c, r));
        }
        return a;
      }
      function ic(e) {
        return void 0 !== e;
      }
      function Cn(e, t = "") {
        const n = _(),
          r = G(),
          i = e + z,
          o = r.firstCreatePass ? bi(r, i, 1, t, null) : r.data[i],
          s = gv(r, n, o, t, e);
        (n[i] = s), ia() && Ca(r, n, s, o), en(o, !1);
      }
      let gv = (e, t, n, r, i) => (
        Un(!0),
        (function _a(e, t) {
          return e.createText(t);
        })(t[j], r)
      );
      function Yd(e) {
        return Xd("", e, ""), Yd;
      }
      function Xd(e, t, n) {
        const r = _(),
          i = (function vi(e, t, n, r) {
            return Ue(e, Kr(), n) ? t + L(n) + r : B;
          })(r, e, t, n);
        return (
          i !== B &&
            (function En(e, t, n) {
              const r = ra(t, e);
              !(function Ug(e, t, n) {
                e.setValue(t, n);
              })(e[j], r, n);
            })(r, Ze(), i),
          Xd
        );
      }
      const Ni = "en-US";
      let jv = Ni;
      class vr {}
      class u_ {}
      class af extends vr {
        constructor(t, n, r) {
          super(),
            (this._parent = n),
            (this._bootstrapComponents = []),
            (this.destroyCbs = []),
            (this.componentFactoryResolver = new yy(this));
          const i = dt(t);
          (this._bootstrapComponents = wn(i.bootstrap)),
            (this._r3Injector = Rb(
              t,
              n,
              [
                { provide: vr, useValue: this },
                { provide: Ba, useValue: this.componentFactoryResolver },
                ...r,
              ],
              Ce(t),
              new Set(["environment"]),
            )),
            this._r3Injector.resolveInjectorInitializers(),
            (this.instance = this._r3Injector.get(t));
        }
        get injector() {
          return this._r3Injector;
        }
        destroy() {
          const t = this._r3Injector;
          !t.destroyed && t.destroy(),
            this.destroyCbs.forEach((n) => n()),
            (this.destroyCbs = null);
        }
        onDestroy(t) {
          this.destroyCbs.push(t);
        }
      }
      class cf extends u_ {
        constructor(t) {
          super(), (this.moduleType = t);
        }
        create(t) {
          return new af(this.moduleType, t, []);
        }
      }
      class d_ extends vr {
        constructor(t) {
          super(),
            (this.componentFactoryResolver = new yy(this)),
            (this.instance = null);
          const n = new ci(
            [
              ...t.providers,
              { provide: vr, useValue: this },
              { provide: Ba, useValue: this.componentFactoryResolver },
            ],
            t.parent || Ra(),
            t.debugName,
            new Set(["environment"]),
          );
          (this.injector = n),
            t.runEnvironmentInitializers && n.resolveInjectorInitializers();
        }
        destroy() {
          this.injector.destroy();
        }
        onDestroy(t) {
          this.injector.onDestroy(t);
        }
      }
      function lf(e, t, n = null) {
        return new d_({
          providers: e,
          parent: t,
          debugName: n,
          runEnvironmentInitializers: !0,
        }).injector;
      }
      let v1 = (() => {
        class e {
          constructor(n) {
            (this._injector = n), (this.cachedInjectors = new Map());
          }
          getOrCreateStandaloneInjector(n) {
            if (!n.standalone) return null;
            if (!this.cachedInjectors.has(n)) {
              const r = bb(0, n.type),
                i =
                  r.length > 0
                    ? lf([r], this._injector, `Standalone[${n.type.name}]`)
                    : null;
              this.cachedInjectors.set(n, i);
            }
            return this.cachedInjectors.get(n);
          }
          ngOnDestroy() {
            try {
              for (const n of this.cachedInjectors.values())
                null !== n && n.destroy();
            } finally {
              this.cachedInjectors.clear();
            }
          }
          static {
            this.ɵprov = S({
              token: e,
              providedIn: "environment",
              factory: () => new e(D(mt)),
            });
          }
        }
        return e;
      })();
      function f_(e) {
        e.getStandaloneInjector = (t) =>
          t.get(v1).getOrCreateStandaloneInjector(e);
      }
      function W1(e, t, n, r = !0) {
        const i = t[I];
        if (
          ((function fx(e, t, n, r) {
            const i = Oe + r,
              o = n.length;
            r > 0 && (n[i - 1][jt] = t),
              r < o - Oe
                ? ((t[jt] = n[i]), yg(n, Oe + r, t))
                : (n.push(t), (t[jt] = null)),
              (t[de] = n);
            const s = t[lo];
            null !== s &&
              n !== s &&
              (function hx(e, t) {
                const n = e[zr];
                t[ve] !== t[de][de][ve] && (e[bm] = !0),
                  null === n ? (e[zr] = [t]) : n.push(t);
              })(s, t);
            const a = t[Yt];
            null !== a && a.insertView(e), (t[V] |= 128);
          })(i, t, e, n),
          r)
        ) {
          const o = qu(n, e),
            s = t[j],
            a = Ea(s, e[Xt]);
          null !== a &&
            (function lx(e, t, n, r, i, o) {
              (r[me] = i), (r[Ve] = t), To(e, r, n, 1, i, o);
            })(i, e[Ve], s, t, a, o);
        }
      }
      let In = (() => {
        class e {
          static {
            this.__NG_ELEMENT_ID__ = Q1;
          }
        }
        return e;
      })();
      const K1 = In,
        Z1 = class extends K1 {
          constructor(t, n, r) {
            super(),
              (this._declarationLView = t),
              (this._declarationTContainer = n),
              (this.elementRef = r);
          }
          get ssrId() {
            return this._declarationTContainer.tView?.ssrId || null;
          }
          createEmbeddedView(t, n) {
            return this.createEmbeddedViewImpl(t, n);
          }
          createEmbeddedViewImpl(t, n, r) {
            const i = (function G1(e, t, n, r) {
              const i = t.tView,
                a = za(
                  e,
                  i,
                  n,
                  4096 & e[V] ? 4096 : 16,
                  null,
                  t,
                  null,
                  null,
                  null,
                  r?.injector ?? null,
                  r?.hydrationInfo ?? null,
                );
              a[lo] = e[t.index];
              const l = e[Yt];
              return (
                null !== l && (a[Yt] = l.createEmbeddedView(i)), Fd(i, a, n), a
              );
            })(this._declarationLView, this._declarationTContainer, t, {
              injector: n,
              hydrationInfo: r,
            });
            return new Vo(i);
          }
        };
      function Q1() {
        return (function lc(e, t) {
          return 4 & e.type ? new Z1(t, e, fi(e, t)) : null;
        })(ke(), _());
      }
      let Ut = (() => {
        class e {
          static {
            this.__NG_ELEMENT_ID__ = nO;
          }
        }
        return e;
      })();
      function nO() {
        return (function A_(e, t) {
          let n;
          const r = t[e.index];
          return (
            We(r)
              ? (n = r)
              : ((n = sy(r, t, null, e)), (t[e.index] = n), qa(t, n)),
            N_(n, t, e, r),
            new x_(n, e, t)
          );
        })(ke(), _());
      }
      const rO = Ut,
        x_ = class extends rO {
          constructor(t, n, r) {
            super(),
              (this._lContainer = t),
              (this._hostTNode = n),
              (this._hostLView = r);
          }
          get element() {
            return fi(this._hostTNode, this._hostLView);
          }
          get injector() {
            return new Qe(this._hostTNode, this._hostLView);
          }
          get parentInjector() {
            const t = ua(this._hostTNode, this._hostLView);
            if (Cu(t)) {
              const n = vo(t, this._hostLView),
                r = yo(t);
              return new Qe(n[I].data[r + 8], n);
            }
            return new Qe(null, this._hostLView);
          }
          clear() {
            for (; this.length > 0; ) this.remove(this.length - 1);
          }
          get(t) {
            const n = T_(this._lContainer);
            return (null !== n && n[t]) || null;
          }
          get length() {
            return this._lContainer.length - Oe;
          }
          createEmbeddedView(t, n, r) {
            let i, o;
            "number" == typeof r
              ? (i = r)
              : null != r && ((i = r.index), (o = r.injector));
            const a = t.createEmbeddedViewImpl(n || {}, o, null);
            return this.insertImpl(a, i, false), a;
          }
          createComponent(t, n, r, i, o) {
            const s =
              t &&
              !(function wo(e) {
                return "function" == typeof e;
              })(t);
            let a;
            if (s) a = n;
            else {
              const m = n || {};
              (a = m.index),
                (r = m.injector),
                (i = m.projectableNodes),
                (o = m.environmentInjector || m.ngModuleRef);
            }
            const c = s ? t : new $o(q(t)),
              l = r || this.parentInjector;
            if (!o && null == c.ngModule) {
              const g = (s ? l : this.parentInjector).get(mt, null);
              g && (o = g);
            }
            q(c.componentType ?? {});
            const h = c.create(l, i, null, o);
            return this.insertImpl(h.hostView, a, false), h;
          }
          insert(t, n) {
            return this.insertImpl(t, n, !1);
          }
          insertImpl(t, n, r) {
            const i = t._lView;
            if (
              (function kM(e) {
                return We(e[de]);
              })(i)
            ) {
              const c = this.indexOf(t);
              if (-1 !== c) this.detach(c);
              else {
                const l = i[de],
                  u = new x_(l, l[Ve], l[de]);
                u.detach(u.indexOf(t));
              }
            }
            const s = this._adjustIndex(n),
              a = this._lContainer;
            return (
              W1(a, i, s, !r), t.attachToViewContainerRef(), yg(df(a), s, t), t
            );
          }
          move(t, n) {
            return this.insert(t, n);
          }
          indexOf(t) {
            const n = T_(this._lContainer);
            return null !== n ? n.indexOf(t) : -1;
          }
          remove(t) {
            const n = this._adjustIndex(t, -1),
              r = wa(this._lContainer, n);
            r && (fa(df(this._lContainer), n), $u(r[I], r));
          }
          detach(t) {
            const n = this._adjustIndex(t, -1),
              r = wa(this._lContainer, n);
            return r && null != fa(df(this._lContainer), n) ? new Vo(r) : null;
          }
          _adjustIndex(t, n = 0) {
            return t ?? this.length + n;
          }
        };
      function T_(e) {
        return e[8];
      }
      function df(e) {
        return e[8] || (e[8] = []);
      }
      let N_ = function R_(e, t, n, r) {
        if (e[Xt]) return;
        let i;
        (i =
          8 & n.type
            ? se(r)
            : (function iO(e, t) {
                const n = e[j],
                  r = n.createComment(""),
                  i = it(t, e);
                return (
                  fr(
                    n,
                    Ea(n, i),
                    r,
                    (function bx(e, t) {
                      return e.nextSibling(t);
                    })(n, i),
                    !1,
                  ),
                  r
                );
              })(t, n)),
          (e[Xt] = i);
      };
      const wf = new E("Application Initializer");
      let Ef = (() => {
          class e {
            constructor() {
              (this.initialized = !1),
                (this.done = !1),
                (this.donePromise = new Promise((n, r) => {
                  (this.resolve = n), (this.reject = r);
                })),
                (this.appInits = C(wf, { optional: !0 }) ?? []);
            }
            runInitializers() {
              if (this.initialized) return;
              const n = [];
              for (const i of this.appInits) {
                const o = i();
                if (tc(o)) n.push(o);
                else if (Uy(o)) {
                  const s = new Promise((a, c) => {
                    o.subscribe({ complete: a, error: c });
                  });
                  n.push(s);
                }
              }
              const r = () => {
                (this.done = !0), this.resolve();
              };
              Promise.all(n)
                .then(() => {
                  r();
                })
                .catch((i) => {
                  this.reject(i);
                }),
                0 === n.length && r(),
                (this.initialized = !0);
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
            }
          }
          return e;
        })(),
        r0 = (() => {
          class e {
            log(n) {
              console.log(n);
            }
            warn(n) {
              console.warn(n);
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵprov = S({
                token: e,
                factory: e.ɵfac,
                providedIn: "platform",
              });
            }
          }
          return e;
        })();
      const cn = new E("LocaleId", {
        providedIn: "root",
        factory: () =>
          C(cn, H.Optional | H.SkipSelf) ||
          (function kO() {
            return (typeof $localize < "u" && $localize.locale) || Ni;
          })(),
      });
      let fc = (() => {
        class e {
          constructor() {
            (this.taskId = 0),
              (this.pendingTasks = new Set()),
              (this.hasPendingTasks = new lt(!1));
          }
          add() {
            this.hasPendingTasks.next(!0);
            const n = this.taskId++;
            return this.pendingTasks.add(n), n;
          }
          remove(n) {
            this.pendingTasks.delete(n),
              0 === this.pendingTasks.size && this.hasPendingTasks.next(!1);
          }
          ngOnDestroy() {
            this.pendingTasks.clear(), this.hasPendingTasks.next(!1);
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      class jO {
        constructor(t, n) {
          (this.ngModuleFactory = t), (this.componentFactories = n);
        }
      }
      let o0 = (() => {
        class e {
          compileModuleSync(n) {
            return new cf(n);
          }
          compileModuleAsync(n) {
            return Promise.resolve(this.compileModuleSync(n));
          }
          compileModuleAndAllComponentsSync(n) {
            const r = this.compileModuleSync(n),
              o = wn(dt(n).declarations).reduce((s, a) => {
                const c = q(a);
                return c && s.push(new $o(c)), s;
              }, []);
            return new jO(r, o);
          }
          compileModuleAndAllComponentsAsync(n) {
            return Promise.resolve(this.compileModuleAndAllComponentsSync(n));
          }
          clearCache() {}
          clearCacheFor(n) {}
          getModuleId(n) {}
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      const l0 = new E(""),
        pc = new E("");
      let xf,
        Mf = (() => {
          class e {
            constructor(n, r, i) {
              (this._ngZone = n),
                (this.registry = r),
                (this._pendingCount = 0),
                (this._isZoneStable = !0),
                (this._didWork = !1),
                (this._callbacks = []),
                (this.taskTrackingZone = null),
                xf ||
                  ((function sP(e) {
                    xf = e;
                  })(i),
                  i.addToWindow(r)),
                this._watchAngularEvents(),
                n.run(() => {
                  this.taskTrackingZone =
                    typeof Zone > "u"
                      ? null
                      : Zone.current.get("TaskTrackingZone");
                });
            }
            _watchAngularEvents() {
              this._ngZone.onUnstable.subscribe({
                next: () => {
                  (this._didWork = !0), (this._isZoneStable = !1);
                },
              }),
                this._ngZone.runOutsideAngular(() => {
                  this._ngZone.onStable.subscribe({
                    next: () => {
                      W.assertNotInAngularZone(),
                        queueMicrotask(() => {
                          (this._isZoneStable = !0),
                            this._runCallbacksIfReady();
                        });
                    },
                  });
                });
            }
            increasePendingRequestCount() {
              return (
                (this._pendingCount += 1),
                (this._didWork = !0),
                this._pendingCount
              );
            }
            decreasePendingRequestCount() {
              if (((this._pendingCount -= 1), this._pendingCount < 0))
                throw new Error("pending async requests below zero");
              return this._runCallbacksIfReady(), this._pendingCount;
            }
            isStable() {
              return (
                this._isZoneStable &&
                0 === this._pendingCount &&
                !this._ngZone.hasPendingMacrotasks
              );
            }
            _runCallbacksIfReady() {
              if (this.isStable())
                queueMicrotask(() => {
                  for (; 0 !== this._callbacks.length; ) {
                    let n = this._callbacks.pop();
                    clearTimeout(n.timeoutId), n.doneCb(this._didWork);
                  }
                  this._didWork = !1;
                });
              else {
                let n = this.getPendingTasks();
                (this._callbacks = this._callbacks.filter(
                  (r) =>
                    !r.updateCb ||
                    !r.updateCb(n) ||
                    (clearTimeout(r.timeoutId), !1),
                )),
                  (this._didWork = !0);
              }
            }
            getPendingTasks() {
              return this.taskTrackingZone
                ? this.taskTrackingZone.macroTasks.map((n) => ({
                    source: n.source,
                    creationLocation: n.creationLocation,
                    data: n.data,
                  }))
                : [];
            }
            addCallback(n, r, i) {
              let o = -1;
              r &&
                r > 0 &&
                (o = setTimeout(() => {
                  (this._callbacks = this._callbacks.filter(
                    (s) => s.timeoutId !== o,
                  )),
                    n(this._didWork, this.getPendingTasks());
                }, r)),
                this._callbacks.push({ doneCb: n, timeoutId: o, updateCb: i });
            }
            whenStable(n, r, i) {
              if (i && !this.taskTrackingZone)
                throw new Error(
                  'Task tracking zone is required when passing an update callback to whenStable(). Is "zone.js/plugins/task-tracking" loaded?',
                );
              this.addCallback(n, r, i), this._runCallbacksIfReady();
            }
            getPendingRequestCount() {
              return this._pendingCount;
            }
            registerApplication(n) {
              this.registry.registerApplication(n, this);
            }
            unregisterApplication(n) {
              this.registry.unregisterApplication(n);
            }
            findProviders(n, r, i) {
              return [];
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(W), D(Sf), D(pc));
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac });
            }
          }
          return e;
        })(),
        Sf = (() => {
          class e {
            constructor() {
              this._applications = new Map();
            }
            registerApplication(n, r) {
              this._applications.set(n, r);
            }
            unregisterApplication(n) {
              this._applications.delete(n);
            }
            unregisterAllApplications() {
              this._applications.clear();
            }
            getTestability(n) {
              return this._applications.get(n) || null;
            }
            getAllTestabilities() {
              return Array.from(this._applications.values());
            }
            getAllRootElements() {
              return Array.from(this._applications.keys());
            }
            findTestabilityInTree(n, r = !0) {
              return xf?.findTestabilityInTree(this, n, r) ?? null;
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵprov = S({
                token: e,
                factory: e.ɵfac,
                providedIn: "platform",
              });
            }
          }
          return e;
        })(),
        Wn = null;
      const u0 = new E("AllowMultipleToken"),
        Tf = new E("PlatformDestroyListeners"),
        Af = new E("appBootstrapListener");
      class f0 {
        constructor(t, n) {
          (this.name = t), (this.token = n);
        }
      }
      function p0(e, t, n = []) {
        const r = `Platform: ${t}`,
          i = new E(r);
        return (o = []) => {
          let s = Nf();
          if (!s || s.injector.get(u0, !1)) {
            const a = [...n, ...o, { provide: i, useValue: !0 }];
            e
              ? e(a)
              : (function lP(e) {
                  if (Wn && !Wn.get(u0, !1)) throw new v(400, !1);
                  (function d0() {
                    !(function _M(e) {
                      Tm = e;
                    })(() => {
                      throw new v(600, !1);
                    });
                  })(),
                    (Wn = e);
                  const t = e.get(g0);
                  (function h0(e) {
                    e.get(wb, null)?.forEach((n) => n());
                  })(e);
                })(
                  (function m0(e = [], t) {
                    return bt.create({
                      name: t,
                      providers: [
                        { provide: rd, useValue: "platform" },
                        { provide: Tf, useValue: new Set([() => (Wn = null)]) },
                        ...e,
                      ],
                    });
                  })(a, r),
                );
          }
          return (function dP(e) {
            const t = Nf();
            if (!t) throw new v(401, !1);
            return t;
          })();
        };
      }
      function Nf() {
        return Wn?.get(g0) ?? null;
      }
      let g0 = (() => {
        class e {
          constructor(n) {
            (this._injector = n),
              (this._modules = []),
              (this._destroyListeners = []),
              (this._destroyed = !1);
          }
          bootstrapModuleFactory(n, r) {
            const i = (function fP(e = "zone.js", t) {
              return "noop" === e ? new LT() : "zone.js" === e ? new W(t) : e;
            })(
              r?.ngZone,
              (function b0(e) {
                return {
                  enableLongStackTrace: !1,
                  shouldCoalesceEventChangeDetection: e?.eventCoalescing ?? !1,
                  shouldCoalesceRunChangeDetection: e?.runCoalescing ?? !1,
                };
              })({
                eventCoalescing: r?.ngZoneEventCoalescing,
                runCoalescing: r?.ngZoneRunCoalescing,
              }),
            );
            return i.run(() => {
              const o = (function y1(e, t, n) {
                  return new af(e, t, n);
                })(
                  n.moduleType,
                  this.injector,
                  (function w0(e) {
                    return [
                      { provide: W, useFactory: e },
                      {
                        provide: Ro,
                        multi: !0,
                        useFactory: () => {
                          const t = C(pP, { optional: !0 });
                          return () => t.initialize();
                        },
                      },
                      { provide: D0, useFactory: hP },
                      { provide: Lb, useFactory: jb },
                    ];
                  })(() => i),
                ),
                s = o.injector.get(xt, null);
              return (
                i.runOutsideAngular(() => {
                  const a = i.onError.subscribe({
                    next: (c) => {
                      s.handleError(c);
                    },
                  });
                  o.onDestroy(() => {
                    mc(this._modules, o), a.unsubscribe();
                  });
                }),
                (function y0(e, t, n) {
                  try {
                    const r = n();
                    return tc(r)
                      ? r.catch((i) => {
                          throw (
                            (t.runOutsideAngular(() => e.handleError(i)), i)
                          );
                        })
                      : r;
                  } catch (r) {
                    throw (t.runOutsideAngular(() => e.handleError(r)), r);
                  }
                })(s, i, () => {
                  const a = o.injector.get(Ef);
                  return (
                    a.runInitializers(),
                    a.donePromise.then(
                      () => (
                        (function Bv(e) {
                          Ct(e, "Expected localeId to be defined"),
                            "string" == typeof e &&
                              (jv = e.toLowerCase().replace(/_/g, "-"));
                        })(o.injector.get(cn, Ni) || Ni),
                        this._moduleDoBootstrap(o),
                        o
                      ),
                    )
                  );
                })
              );
            });
          }
          bootstrapModule(n, r = []) {
            const i = v0({}, r);
            return (function aP(e, t, n) {
              const r = new cf(n);
              return Promise.resolve(r);
            })(0, 0, n).then((o) => this.bootstrapModuleFactory(o, i));
          }
          _moduleDoBootstrap(n) {
            const r = n.injector.get(_r);
            if (n._bootstrapComponents.length > 0)
              n._bootstrapComponents.forEach((i) => r.bootstrap(i));
            else {
              if (!n.instance.ngDoBootstrap) throw new v(-403, !1);
              n.instance.ngDoBootstrap(r);
            }
            this._modules.push(n);
          }
          onDestroy(n) {
            this._destroyListeners.push(n);
          }
          get injector() {
            return this._injector;
          }
          destroy() {
            if (this._destroyed) throw new v(404, !1);
            this._modules.slice().forEach((r) => r.destroy()),
              this._destroyListeners.forEach((r) => r());
            const n = this._injector.get(Tf, null);
            n && (n.forEach((r) => r()), n.clear()), (this._destroyed = !0);
          }
          get destroyed() {
            return this._destroyed;
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(bt));
            };
          }
          static {
            this.ɵprov = S({
              token: e,
              factory: e.ɵfac,
              providedIn: "platform",
            });
          }
        }
        return e;
      })();
      function v0(e, t) {
        return Array.isArray(t) ? t.reduce(v0, e) : { ...e, ...t };
      }
      let _r = (() => {
        class e {
          constructor() {
            (this._bootstrapListeners = []),
              (this._runningTick = !1),
              (this._destroyed = !1),
              (this._destroyListeners = []),
              (this._views = []),
              (this.internalErrorHandler = C(D0)),
              (this.zoneIsStable = C(Lb)),
              (this.componentTypes = []),
              (this.components = []),
              (this.isStable = C(fc).hasPendingTasks.pipe(
                Ft((n) => (n ? A(!1) : this.zoneIsStable)),
                Wp(),
                $l(),
              )),
              (this._injector = C(mt));
          }
          get destroyed() {
            return this._destroyed;
          }
          get injector() {
            return this._injector;
          }
          bootstrap(n, r) {
            const i = n instanceof Mb;
            if (!this._injector.get(Ef).done)
              throw (
                (!i &&
                  (function Br(e) {
                    const t = q(e) || Re(e) || Ge(e);
                    return null !== t && t.standalone;
                  })(n),
                new v(405, !1))
              );
            let s;
            (s = i ? n : this._injector.get(Ba).resolveComponentFactory(n)),
              this.componentTypes.push(s.componentType);
            const a = (function cP(e) {
                return e.isBoundToModule;
              })(s)
                ? void 0
                : this._injector.get(vr),
              l = s.create(bt.NULL, [], r || s.selector, a),
              u = l.location.nativeElement,
              d = l.injector.get(l0, null);
            return (
              d?.registerApplication(u),
              l.onDestroy(() => {
                this.detachView(l.hostView),
                  mc(this.components, l),
                  d?.unregisterApplication(u);
              }),
              this._loadComponent(l),
              l
            );
          }
          tick() {
            if (this._runningTick) throw new v(101, !1);
            try {
              this._runningTick = !0;
              for (let n of this._views) n.detectChanges();
            } catch (n) {
              this.internalErrorHandler(n);
            } finally {
              this._runningTick = !1;
            }
          }
          attachView(n) {
            const r = n;
            this._views.push(r), r.attachToAppRef(this);
          }
          detachView(n) {
            const r = n;
            mc(this._views, r), r.detachFromAppRef();
          }
          _loadComponent(n) {
            this.attachView(n.hostView), this.tick(), this.components.push(n);
            const r = this._injector.get(Af, []);
            r.push(...this._bootstrapListeners), r.forEach((i) => i(n));
          }
          ngOnDestroy() {
            if (!this._destroyed)
              try {
                this._destroyListeners.forEach((n) => n()),
                  this._views.slice().forEach((n) => n.destroy());
              } finally {
                (this._destroyed = !0),
                  (this._views = []),
                  (this._bootstrapListeners = []),
                  (this._destroyListeners = []);
              }
          }
          onDestroy(n) {
            return (
              this._destroyListeners.push(n),
              () => mc(this._destroyListeners, n)
            );
          }
          destroy() {
            if (this._destroyed) throw new v(406, !1);
            const n = this._injector;
            n.destroy && !n.destroyed && n.destroy();
          }
          get viewCount() {
            return this._views.length;
          }
          warnIfDestroyed() {}
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      function mc(e, t) {
        const n = e.indexOf(t);
        n > -1 && e.splice(n, 1);
      }
      const D0 = new E("", {
        providedIn: "root",
        factory: () => C(xt).handleError.bind(void 0),
      });
      function hP() {
        const e = C(W),
          t = C(xt);
        return (n) => e.runOutsideAngular(() => t.handleError(n));
      }
      let pP = (() => {
        class e {
          constructor() {
            (this.zone = C(W)), (this.applicationRef = C(_r));
          }
          initialize() {
            this._onMicrotaskEmptySubscription ||
              (this._onMicrotaskEmptySubscription =
                this.zone.onMicrotaskEmpty.subscribe({
                  next: () => {
                    this.zone.run(() => {
                      this.applicationRef.tick();
                    });
                  },
                }));
          }
          ngOnDestroy() {
            this._onMicrotaskEmptySubscription?.unsubscribe();
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      let Rf = (() => {
        class e {
          static {
            this.__NG_ELEMENT_ID__ = gP;
          }
        }
        return e;
      })();
      function gP(e) {
        return (function bP(e, t, n) {
          if (sr(e) && !n) {
            const r = ft(e.index, t);
            return new Vo(r, r);
          }
          return 47 & e.type ? new Vo(t[ve], t) : null;
        })(ke(), _(), 16 == (16 & e));
      }
      class S0 {
        constructor() {}
        supports(t) {
          return Za(t);
        }
        create(t) {
          return new wP(t);
        }
      }
      const DP = (e, t) => t;
      class wP {
        constructor(t) {
          (this.length = 0),
            (this._linkedRecords = null),
            (this._unlinkedRecords = null),
            (this._previousItHead = null),
            (this._itHead = null),
            (this._itTail = null),
            (this._additionsHead = null),
            (this._additionsTail = null),
            (this._movesHead = null),
            (this._movesTail = null),
            (this._removalsHead = null),
            (this._removalsTail = null),
            (this._identityChangesHead = null),
            (this._identityChangesTail = null),
            (this._trackByFn = t || DP);
        }
        forEachItem(t) {
          let n;
          for (n = this._itHead; null !== n; n = n._next) t(n);
        }
        forEachOperation(t) {
          let n = this._itHead,
            r = this._removalsHead,
            i = 0,
            o = null;
          for (; n || r; ) {
            const s = !r || (n && n.currentIndex < T0(r, i, o)) ? n : r,
              a = T0(s, i, o),
              c = s.currentIndex;
            if (s === r) i--, (r = r._nextRemoved);
            else if (((n = n._next), null == s.previousIndex)) i++;
            else {
              o || (o = []);
              const l = a - i,
                u = c - i;
              if (l != u) {
                for (let f = 0; f < l; f++) {
                  const h = f < o.length ? o[f] : (o[f] = 0),
                    p = h + f;
                  u <= p && p < l && (o[f] = h + 1);
                }
                o[s.previousIndex] = u - l;
              }
            }
            a !== c && t(s, a, c);
          }
        }
        forEachPreviousItem(t) {
          let n;
          for (n = this._previousItHead; null !== n; n = n._nextPrevious) t(n);
        }
        forEachAddedItem(t) {
          let n;
          for (n = this._additionsHead; null !== n; n = n._nextAdded) t(n);
        }
        forEachMovedItem(t) {
          let n;
          for (n = this._movesHead; null !== n; n = n._nextMoved) t(n);
        }
        forEachRemovedItem(t) {
          let n;
          for (n = this._removalsHead; null !== n; n = n._nextRemoved) t(n);
        }
        forEachIdentityChange(t) {
          let n;
          for (
            n = this._identityChangesHead;
            null !== n;
            n = n._nextIdentityChange
          )
            t(n);
        }
        diff(t) {
          if ((null == t && (t = []), !Za(t))) throw new v(900, !1);
          return this.check(t) ? this : null;
        }
        onDestroy() {}
        check(t) {
          this._reset();
          let i,
            o,
            s,
            n = this._itHead,
            r = !1;
          if (Array.isArray(t)) {
            this.length = t.length;
            for (let a = 0; a < this.length; a++)
              (o = t[a]),
                (s = this._trackByFn(a, o)),
                null !== n && Object.is(n.trackById, s)
                  ? (r && (n = this._verifyReinsertion(n, o, s, a)),
                    Object.is(n.item, o) || this._addIdentityChange(n, o))
                  : ((n = this._mismatch(n, o, s, a)), (r = !0)),
                (n = n._next);
          } else
            (i = 0),
              (function WA(e, t) {
                if (Array.isArray(e))
                  for (let n = 0; n < e.length; n++) t(e[n]);
                else {
                  const n = e[Symbol.iterator]();
                  let r;
                  for (; !(r = n.next()).done; ) t(r.value);
                }
              })(t, (a) => {
                (s = this._trackByFn(i, a)),
                  null !== n && Object.is(n.trackById, s)
                    ? (r && (n = this._verifyReinsertion(n, a, s, i)),
                      Object.is(n.item, a) || this._addIdentityChange(n, a))
                    : ((n = this._mismatch(n, a, s, i)), (r = !0)),
                  (n = n._next),
                  i++;
              }),
              (this.length = i);
          return this._truncate(n), (this.collection = t), this.isDirty;
        }
        get isDirty() {
          return (
            null !== this._additionsHead ||
            null !== this._movesHead ||
            null !== this._removalsHead ||
            null !== this._identityChangesHead
          );
        }
        _reset() {
          if (this.isDirty) {
            let t;
            for (
              t = this._previousItHead = this._itHead;
              null !== t;
              t = t._next
            )
              t._nextPrevious = t._next;
            for (t = this._additionsHead; null !== t; t = t._nextAdded)
              t.previousIndex = t.currentIndex;
            for (
              this._additionsHead = this._additionsTail = null,
                t = this._movesHead;
              null !== t;
              t = t._nextMoved
            )
              t.previousIndex = t.currentIndex;
            (this._movesHead = this._movesTail = null),
              (this._removalsHead = this._removalsTail = null),
              (this._identityChangesHead = this._identityChangesTail = null);
          }
        }
        _mismatch(t, n, r, i) {
          let o;
          return (
            null === t ? (o = this._itTail) : ((o = t._prev), this._remove(t)),
            null !==
            (t =
              null === this._unlinkedRecords
                ? null
                : this._unlinkedRecords.get(r, null))
              ? (Object.is(t.item, n) || this._addIdentityChange(t, n),
                this._reinsertAfter(t, o, i))
              : null !==
                (t =
                  null === this._linkedRecords
                    ? null
                    : this._linkedRecords.get(r, i))
              ? (Object.is(t.item, n) || this._addIdentityChange(t, n),
                this._moveAfter(t, o, i))
              : (t = this._addAfter(new EP(n, r), o, i)),
            t
          );
        }
        _verifyReinsertion(t, n, r, i) {
          let o =
            null === this._unlinkedRecords
              ? null
              : this._unlinkedRecords.get(r, null);
          return (
            null !== o
              ? (t = this._reinsertAfter(o, t._prev, i))
              : t.currentIndex != i &&
                ((t.currentIndex = i), this._addToMoves(t, i)),
            t
          );
        }
        _truncate(t) {
          for (; null !== t; ) {
            const n = t._next;
            this._addToRemovals(this._unlink(t)), (t = n);
          }
          null !== this._unlinkedRecords && this._unlinkedRecords.clear(),
            null !== this._additionsTail &&
              (this._additionsTail._nextAdded = null),
            null !== this._movesTail && (this._movesTail._nextMoved = null),
            null !== this._itTail && (this._itTail._next = null),
            null !== this._removalsTail &&
              (this._removalsTail._nextRemoved = null),
            null !== this._identityChangesTail &&
              (this._identityChangesTail._nextIdentityChange = null);
        }
        _reinsertAfter(t, n, r) {
          null !== this._unlinkedRecords && this._unlinkedRecords.remove(t);
          const i = t._prevRemoved,
            o = t._nextRemoved;
          return (
            null === i ? (this._removalsHead = o) : (i._nextRemoved = o),
            null === o ? (this._removalsTail = i) : (o._prevRemoved = i),
            this._insertAfter(t, n, r),
            this._addToMoves(t, r),
            t
          );
        }
        _moveAfter(t, n, r) {
          return (
            this._unlink(t),
            this._insertAfter(t, n, r),
            this._addToMoves(t, r),
            t
          );
        }
        _addAfter(t, n, r) {
          return (
            this._insertAfter(t, n, r),
            (this._additionsTail =
              null === this._additionsTail
                ? (this._additionsHead = t)
                : (this._additionsTail._nextAdded = t)),
            t
          );
        }
        _insertAfter(t, n, r) {
          const i = null === n ? this._itHead : n._next;
          return (
            (t._next = i),
            (t._prev = n),
            null === i ? (this._itTail = t) : (i._prev = t),
            null === n ? (this._itHead = t) : (n._next = t),
            null === this._linkedRecords && (this._linkedRecords = new x0()),
            this._linkedRecords.put(t),
            (t.currentIndex = r),
            t
          );
        }
        _remove(t) {
          return this._addToRemovals(this._unlink(t));
        }
        _unlink(t) {
          null !== this._linkedRecords && this._linkedRecords.remove(t);
          const n = t._prev,
            r = t._next;
          return (
            null === n ? (this._itHead = r) : (n._next = r),
            null === r ? (this._itTail = n) : (r._prev = n),
            t
          );
        }
        _addToMoves(t, n) {
          return (
            t.previousIndex === n ||
              (this._movesTail =
                null === this._movesTail
                  ? (this._movesHead = t)
                  : (this._movesTail._nextMoved = t)),
            t
          );
        }
        _addToRemovals(t) {
          return (
            null === this._unlinkedRecords &&
              (this._unlinkedRecords = new x0()),
            this._unlinkedRecords.put(t),
            (t.currentIndex = null),
            (t._nextRemoved = null),
            null === this._removalsTail
              ? ((this._removalsTail = this._removalsHead = t),
                (t._prevRemoved = null))
              : ((t._prevRemoved = this._removalsTail),
                (this._removalsTail = this._removalsTail._nextRemoved = t)),
            t
          );
        }
        _addIdentityChange(t, n) {
          return (
            (t.item = n),
            (this._identityChangesTail =
              null === this._identityChangesTail
                ? (this._identityChangesHead = t)
                : (this._identityChangesTail._nextIdentityChange = t)),
            t
          );
        }
      }
      class EP {
        constructor(t, n) {
          (this.item = t),
            (this.trackById = n),
            (this.currentIndex = null),
            (this.previousIndex = null),
            (this._nextPrevious = null),
            (this._prev = null),
            (this._next = null),
            (this._prevDup = null),
            (this._nextDup = null),
            (this._prevRemoved = null),
            (this._nextRemoved = null),
            (this._nextAdded = null),
            (this._nextMoved = null),
            (this._nextIdentityChange = null);
        }
      }
      class CP {
        constructor() {
          (this._head = null), (this._tail = null);
        }
        add(t) {
          null === this._head
            ? ((this._head = this._tail = t),
              (t._nextDup = null),
              (t._prevDup = null))
            : ((this._tail._nextDup = t),
              (t._prevDup = this._tail),
              (t._nextDup = null),
              (this._tail = t));
        }
        get(t, n) {
          let r;
          for (r = this._head; null !== r; r = r._nextDup)
            if (
              (null === n || n <= r.currentIndex) &&
              Object.is(r.trackById, t)
            )
              return r;
          return null;
        }
        remove(t) {
          const n = t._prevDup,
            r = t._nextDup;
          return (
            null === n ? (this._head = r) : (n._nextDup = r),
            null === r ? (this._tail = n) : (r._prevDup = n),
            null === this._head
          );
        }
      }
      class x0 {
        constructor() {
          this.map = new Map();
        }
        put(t) {
          const n = t.trackById;
          let r = this.map.get(n);
          r || ((r = new CP()), this.map.set(n, r)), r.add(t);
        }
        get(t, n) {
          const i = this.map.get(t);
          return i ? i.get(t, n) : null;
        }
        remove(t) {
          const n = t.trackById;
          return this.map.get(n).remove(t) && this.map.delete(n), t;
        }
        get isEmpty() {
          return 0 === this.map.size;
        }
        clear() {
          this.map.clear();
        }
      }
      function T0(e, t, n) {
        const r = e.previousIndex;
        if (null === r) return r;
        let i = 0;
        return n && r < n.length && (i = n[r]), r + t + i;
      }
      class A0 {
        constructor() {}
        supports(t) {
          return t instanceof Map || Ld(t);
        }
        create() {
          return new IP();
        }
      }
      class IP {
        constructor() {
          (this._records = new Map()),
            (this._mapHead = null),
            (this._appendAfter = null),
            (this._previousMapHead = null),
            (this._changesHead = null),
            (this._changesTail = null),
            (this._additionsHead = null),
            (this._additionsTail = null),
            (this._removalsHead = null),
            (this._removalsTail = null);
        }
        get isDirty() {
          return (
            null !== this._additionsHead ||
            null !== this._changesHead ||
            null !== this._removalsHead
          );
        }
        forEachItem(t) {
          let n;
          for (n = this._mapHead; null !== n; n = n._next) t(n);
        }
        forEachPreviousItem(t) {
          let n;
          for (n = this._previousMapHead; null !== n; n = n._nextPrevious) t(n);
        }
        forEachChangedItem(t) {
          let n;
          for (n = this._changesHead; null !== n; n = n._nextChanged) t(n);
        }
        forEachAddedItem(t) {
          let n;
          for (n = this._additionsHead; null !== n; n = n._nextAdded) t(n);
        }
        forEachRemovedItem(t) {
          let n;
          for (n = this._removalsHead; null !== n; n = n._nextRemoved) t(n);
        }
        diff(t) {
          if (t) {
            if (!(t instanceof Map || Ld(t))) throw new v(900, !1);
          } else t = new Map();
          return this.check(t) ? this : null;
        }
        onDestroy() {}
        check(t) {
          this._reset();
          let n = this._mapHead;
          if (
            ((this._appendAfter = null),
            this._forEach(t, (r, i) => {
              if (n && n.key === i)
                this._maybeAddToChanges(n, r),
                  (this._appendAfter = n),
                  (n = n._next);
              else {
                const o = this._getOrCreateRecordForKey(i, r);
                n = this._insertBeforeOrAppend(n, o);
              }
            }),
            n)
          ) {
            n._prev && (n._prev._next = null), (this._removalsHead = n);
            for (let r = n; null !== r; r = r._nextRemoved)
              r === this._mapHead && (this._mapHead = null),
                this._records.delete(r.key),
                (r._nextRemoved = r._next),
                (r.previousValue = r.currentValue),
                (r.currentValue = null),
                (r._prev = null),
                (r._next = null);
          }
          return (
            this._changesTail && (this._changesTail._nextChanged = null),
            this._additionsTail && (this._additionsTail._nextAdded = null),
            this.isDirty
          );
        }
        _insertBeforeOrAppend(t, n) {
          if (t) {
            const r = t._prev;
            return (
              (n._next = t),
              (n._prev = r),
              (t._prev = n),
              r && (r._next = n),
              t === this._mapHead && (this._mapHead = n),
              (this._appendAfter = t),
              t
            );
          }
          return (
            this._appendAfter
              ? ((this._appendAfter._next = n), (n._prev = this._appendAfter))
              : (this._mapHead = n),
            (this._appendAfter = n),
            null
          );
        }
        _getOrCreateRecordForKey(t, n) {
          if (this._records.has(t)) {
            const i = this._records.get(t);
            this._maybeAddToChanges(i, n);
            const o = i._prev,
              s = i._next;
            return (
              o && (o._next = s),
              s && (s._prev = o),
              (i._next = null),
              (i._prev = null),
              i
            );
          }
          const r = new MP(t);
          return (
            this._records.set(t, r),
            (r.currentValue = n),
            this._addToAdditions(r),
            r
          );
        }
        _reset() {
          if (this.isDirty) {
            let t;
            for (
              this._previousMapHead = this._mapHead, t = this._previousMapHead;
              null !== t;
              t = t._next
            )
              t._nextPrevious = t._next;
            for (t = this._changesHead; null !== t; t = t._nextChanged)
              t.previousValue = t.currentValue;
            for (t = this._additionsHead; null != t; t = t._nextAdded)
              t.previousValue = t.currentValue;
            (this._changesHead = this._changesTail = null),
              (this._additionsHead = this._additionsTail = null),
              (this._removalsHead = null);
          }
        }
        _maybeAddToChanges(t, n) {
          Object.is(n, t.currentValue) ||
            ((t.previousValue = t.currentValue),
            (t.currentValue = n),
            this._addToChanges(t));
        }
        _addToAdditions(t) {
          null === this._additionsHead
            ? (this._additionsHead = this._additionsTail = t)
            : ((this._additionsTail._nextAdded = t), (this._additionsTail = t));
        }
        _addToChanges(t) {
          null === this._changesHead
            ? (this._changesHead = this._changesTail = t)
            : ((this._changesTail._nextChanged = t), (this._changesTail = t));
        }
        _forEach(t, n) {
          t instanceof Map
            ? t.forEach(n)
            : Object.keys(t).forEach((r) => n(t[r], r));
        }
      }
      class MP {
        constructor(t) {
          (this.key = t),
            (this.previousValue = null),
            (this.currentValue = null),
            (this._nextPrevious = null),
            (this._next = null),
            (this._prev = null),
            (this._nextAdded = null),
            (this._nextRemoved = null),
            (this._nextChanged = null);
        }
      }
      function N0() {
        return new yc([new S0()]);
      }
      let yc = (() => {
        class e {
          static {
            this.ɵprov = S({ token: e, providedIn: "root", factory: N0 });
          }
          constructor(n) {
            this.factories = n;
          }
          static create(n, r) {
            if (null != r) {
              const i = r.factories.slice();
              n = n.concat(i);
            }
            return new e(n);
          }
          static extend(n) {
            return {
              provide: e,
              useFactory: (r) => e.create(n, r || N0()),
              deps: [[e, new Co(), new dr()]],
            };
          }
          find(n) {
            const r = this.factories.find((i) => i.supports(n));
            if (null != r) return r;
            throw new v(901, !1);
          }
        }
        return e;
      })();
      function R0() {
        return new os([new A0()]);
      }
      let os = (() => {
        class e {
          static {
            this.ɵprov = S({ token: e, providedIn: "root", factory: R0 });
          }
          constructor(n) {
            this.factories = n;
          }
          static create(n, r) {
            if (r) {
              const i = r.factories.slice();
              n = n.concat(i);
            }
            return new e(n);
          }
          static extend(n) {
            return {
              provide: e,
              useFactory: (r) => e.create(n, r || R0()),
              deps: [[e, new Co(), new dr()]],
            };
          }
          find(n) {
            const r = this.factories.find((i) => i.supports(n));
            if (r) return r;
            throw new v(901, !1);
          }
        }
        return e;
      })();
      const TP = p0(null, "core", []);
      let AP = (() => {
          class e {
            constructor(n) {}
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(_r));
              };
            }
            static {
              this.ɵmod = Be({ type: e });
            }
            static {
              this.ɵinj = Ne({});
            }
          }
          return e;
        })(),
        Bf = null;
      function Pi() {
        return Bf;
      }
      class zP {}
      const ce = new E("DocumentToken");
      let Vf = (() => {
        class e {
          historyGo(n) {
            throw new Error("Not implemented");
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({
              token: e,
              factory: function () {
                return C(GP);
              },
              providedIn: "platform",
            });
          }
        }
        return e;
      })();
      const qP = new E("Location Initialized");
      let GP = (() => {
        class e extends Vf {
          constructor() {
            super(),
              (this._doc = C(ce)),
              (this._location = window.location),
              (this._history = window.history);
          }
          getBaseHrefFromDOM() {
            return Pi().getBaseHref(this._doc);
          }
          onPopState(n) {
            const r = Pi().getGlobalEventTarget(this._doc, "window");
            return (
              r.addEventListener("popstate", n, !1),
              () => r.removeEventListener("popstate", n)
            );
          }
          onHashChange(n) {
            const r = Pi().getGlobalEventTarget(this._doc, "window");
            return (
              r.addEventListener("hashchange", n, !1),
              () => r.removeEventListener("hashchange", n)
            );
          }
          get href() {
            return this._location.href;
          }
          get protocol() {
            return this._location.protocol;
          }
          get hostname() {
            return this._location.hostname;
          }
          get port() {
            return this._location.port;
          }
          get pathname() {
            return this._location.pathname;
          }
          get search() {
            return this._location.search;
          }
          get hash() {
            return this._location.hash;
          }
          set pathname(n) {
            this._location.pathname = n;
          }
          pushState(n, r, i) {
            this._history.pushState(n, r, i);
          }
          replaceState(n, r, i) {
            this._history.replaceState(n, r, i);
          }
          forward() {
            this._history.forward();
          }
          back() {
            this._history.back();
          }
          historyGo(n = 0) {
            this._history.go(n);
          }
          getState() {
            return this._history.state;
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({
              token: e,
              factory: function () {
                return new e();
              },
              providedIn: "platform",
            });
          }
        }
        return e;
      })();
      function $f(e, t) {
        if (0 == e.length) return t;
        if (0 == t.length) return e;
        let n = 0;
        return (
          e.endsWith("/") && n++,
          t.startsWith("/") && n++,
          2 == n ? e + t.substring(1) : 1 == n ? e + t : e + "/" + t
        );
      }
      function $0(e) {
        const t = e.match(/#|\?|$/),
          n = (t && t.index) || e.length;
        return e.slice(0, n - ("/" === e[n - 1] ? 1 : 0)) + e.slice(n);
      }
      function Mn(e) {
        return e && "?" !== e[0] ? "?" + e : e;
      }
      let wr = (() => {
        class e {
          historyGo(n) {
            throw new Error("Not implemented");
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({
              token: e,
              factory: function () {
                return C(H0);
              },
              providedIn: "root",
            });
          }
        }
        return e;
      })();
      const U0 = new E("appBaseHref");
      let H0 = (() => {
          class e extends wr {
            constructor(n, r) {
              super(),
                (this._platformLocation = n),
                (this._removeListenerFns = []),
                (this._baseHref =
                  r ??
                  this._platformLocation.getBaseHrefFromDOM() ??
                  C(ce).location?.origin ??
                  "");
            }
            ngOnDestroy() {
              for (; this._removeListenerFns.length; )
                this._removeListenerFns.pop()();
            }
            onPopState(n) {
              this._removeListenerFns.push(
                this._platformLocation.onPopState(n),
                this._platformLocation.onHashChange(n),
              );
            }
            getBaseHref() {
              return this._baseHref;
            }
            prepareExternalUrl(n) {
              return $f(this._baseHref, n);
            }
            path(n = !1) {
              const r =
                  this._platformLocation.pathname +
                  Mn(this._platformLocation.search),
                i = this._platformLocation.hash;
              return i && n ? `${r}${i}` : r;
            }
            pushState(n, r, i, o) {
              const s = this.prepareExternalUrl(i + Mn(o));
              this._platformLocation.pushState(n, r, s);
            }
            replaceState(n, r, i, o) {
              const s = this.prepareExternalUrl(i + Mn(o));
              this._platformLocation.replaceState(n, r, s);
            }
            forward() {
              this._platformLocation.forward();
            }
            back() {
              this._platformLocation.back();
            }
            getState() {
              return this._platformLocation.getState();
            }
            historyGo(n = 0) {
              this._platformLocation.historyGo?.(n);
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(Vf), D(U0, 8));
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
            }
          }
          return e;
        })(),
        WP = (() => {
          class e extends wr {
            constructor(n, r) {
              super(),
                (this._platformLocation = n),
                (this._baseHref = ""),
                (this._removeListenerFns = []),
                null != r && (this._baseHref = r);
            }
            ngOnDestroy() {
              for (; this._removeListenerFns.length; )
                this._removeListenerFns.pop()();
            }
            onPopState(n) {
              this._removeListenerFns.push(
                this._platformLocation.onPopState(n),
                this._platformLocation.onHashChange(n),
              );
            }
            getBaseHref() {
              return this._baseHref;
            }
            path(n = !1) {
              let r = this._platformLocation.hash;
              return null == r && (r = "#"), r.length > 0 ? r.substring(1) : r;
            }
            prepareExternalUrl(n) {
              const r = $f(this._baseHref, n);
              return r.length > 0 ? "#" + r : r;
            }
            pushState(n, r, i, o) {
              let s = this.prepareExternalUrl(i + Mn(o));
              0 == s.length && (s = this._platformLocation.pathname),
                this._platformLocation.pushState(n, r, s);
            }
            replaceState(n, r, i, o) {
              let s = this.prepareExternalUrl(i + Mn(o));
              0 == s.length && (s = this._platformLocation.pathname),
                this._platformLocation.replaceState(n, r, s);
            }
            forward() {
              this._platformLocation.forward();
            }
            back() {
              this._platformLocation.back();
            }
            getState() {
              return this._platformLocation.getState();
            }
            historyGo(n = 0) {
              this._platformLocation.historyGo?.(n);
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(Vf), D(U0, 8));
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac });
            }
          }
          return e;
        })(),
        Uf = (() => {
          class e {
            constructor(n) {
              (this._subject = new Ye()),
                (this._urlChangeListeners = []),
                (this._urlChangeSubscription = null),
                (this._locationStrategy = n);
              const r = this._locationStrategy.getBaseHref();
              (this._basePath = (function QP(e) {
                if (new RegExp("^(https?:)?//").test(e)) {
                  const [, n] = e.split(/\/\/[^\/]+/);
                  return n;
                }
                return e;
              })($0(z0(r)))),
                this._locationStrategy.onPopState((i) => {
                  this._subject.emit({
                    url: this.path(!0),
                    pop: !0,
                    state: i.state,
                    type: i.type,
                  });
                });
            }
            ngOnDestroy() {
              this._urlChangeSubscription?.unsubscribe(),
                (this._urlChangeListeners = []);
            }
            path(n = !1) {
              return this.normalize(this._locationStrategy.path(n));
            }
            getState() {
              return this._locationStrategy.getState();
            }
            isCurrentPathEqualTo(n, r = "") {
              return this.path() == this.normalize(n + Mn(r));
            }
            normalize(n) {
              return e.stripTrailingSlash(
                (function ZP(e, t) {
                  if (!e || !t.startsWith(e)) return t;
                  const n = t.substring(e.length);
                  return "" === n || ["/", ";", "?", "#"].includes(n[0])
                    ? n
                    : t;
                })(this._basePath, z0(n)),
              );
            }
            prepareExternalUrl(n) {
              return (
                n && "/" !== n[0] && (n = "/" + n),
                this._locationStrategy.prepareExternalUrl(n)
              );
            }
            go(n, r = "", i = null) {
              this._locationStrategy.pushState(i, "", n, r),
                this._notifyUrlChangeListeners(
                  this.prepareExternalUrl(n + Mn(r)),
                  i,
                );
            }
            replaceState(n, r = "", i = null) {
              this._locationStrategy.replaceState(i, "", n, r),
                this._notifyUrlChangeListeners(
                  this.prepareExternalUrl(n + Mn(r)),
                  i,
                );
            }
            forward() {
              this._locationStrategy.forward();
            }
            back() {
              this._locationStrategy.back();
            }
            historyGo(n = 0) {
              this._locationStrategy.historyGo?.(n);
            }
            onUrlChange(n) {
              return (
                this._urlChangeListeners.push(n),
                this._urlChangeSubscription ||
                  (this._urlChangeSubscription = this.subscribe((r) => {
                    this._notifyUrlChangeListeners(r.url, r.state);
                  })),
                () => {
                  const r = this._urlChangeListeners.indexOf(n);
                  this._urlChangeListeners.splice(r, 1),
                    0 === this._urlChangeListeners.length &&
                      (this._urlChangeSubscription?.unsubscribe(),
                      (this._urlChangeSubscription = null));
                }
              );
            }
            _notifyUrlChangeListeners(n = "", r) {
              this._urlChangeListeners.forEach((i) => i(n, r));
            }
            subscribe(n, r, i) {
              return this._subject.subscribe({
                next: n,
                error: r,
                complete: i,
              });
            }
            static {
              this.normalizeQueryParams = Mn;
            }
            static {
              this.joinWithSlash = $f;
            }
            static {
              this.stripTrailingSlash = $0;
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(wr));
              };
            }
            static {
              this.ɵprov = S({
                token: e,
                factory: function () {
                  return (function KP() {
                    return new Uf(D(wr));
                  })();
                },
                providedIn: "root",
              });
            }
          }
          return e;
        })();
      function z0(e) {
        return e.replace(/\/index.html$/, "");
      }
      function J0(e, t) {
        t = encodeURIComponent(t);
        for (const n of e.split(";")) {
          const r = n.indexOf("="),
            [i, o] = -1 == r ? [n, ""] : [n.slice(0, r), n.slice(r + 1)];
          if (i.trim() === t) return decodeURIComponent(o);
        }
        return null;
      }
      const Xf = /\s+/,
        eD = [];
      let tD = (() => {
          class e {
            constructor(n, r, i, o) {
              (this._iterableDiffers = n),
                (this._keyValueDiffers = r),
                (this._ngEl = i),
                (this._renderer = o),
                (this.initialClasses = eD),
                (this.stateMap = new Map());
            }
            set klass(n) {
              this.initialClasses = null != n ? n.trim().split(Xf) : eD;
            }
            set ngClass(n) {
              this.rawClass = "string" == typeof n ? n.trim().split(Xf) : n;
            }
            ngDoCheck() {
              for (const r of this.initialClasses) this._updateState(r, !0);
              const n = this.rawClass;
              if (Array.isArray(n) || n instanceof Set)
                for (const r of n) this._updateState(r, !0);
              else if (null != n)
                for (const r of Object.keys(n)) this._updateState(r, !!n[r]);
              this._applyStateDiff();
            }
            _updateState(n, r) {
              const i = this.stateMap.get(n);
              void 0 !== i
                ? (i.enabled !== r && ((i.changed = !0), (i.enabled = r)),
                  (i.touched = !0))
                : this.stateMap.set(n, {
                    enabled: r,
                    changed: !0,
                    touched: !0,
                  });
            }
            _applyStateDiff() {
              for (const n of this.stateMap) {
                const r = n[0],
                  i = n[1];
                i.changed
                  ? (this._toggleClass(r, i.enabled), (i.changed = !1))
                  : i.touched ||
                    (i.enabled && this._toggleClass(r, !1),
                    this.stateMap.delete(r)),
                  (i.touched = !1);
              }
            }
            _toggleClass(n, r) {
              (n = n.trim()).length > 0 &&
                n.split(Xf).forEach((i) => {
                  r
                    ? this._renderer.addClass(this._ngEl.nativeElement, i)
                    : this._renderer.removeClass(this._ngEl.nativeElement, i);
                });
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(x(yc), x(os), x(gt), x(Va));
              };
            }
            static {
              this.ɵdir = re({
                type: e,
                selectors: [["", "ngClass", ""]],
                inputs: { klass: ["class", "klass"], ngClass: "ngClass" },
                standalone: !0,
              });
            }
          }
          return e;
        })(),
        iD = (() => {
          class e {
            constructor(n, r) {
              (this._viewContainer = n),
                (this._context = new Lk()),
                (this._thenTemplateRef = null),
                (this._elseTemplateRef = null),
                (this._thenViewRef = null),
                (this._elseViewRef = null),
                (this._thenTemplateRef = r);
            }
            set ngIf(n) {
              (this._context.$implicit = this._context.ngIf = n),
                this._updateView();
            }
            set ngIfThen(n) {
              oD("ngIfThen", n),
                (this._thenTemplateRef = n),
                (this._thenViewRef = null),
                this._updateView();
            }
            set ngIfElse(n) {
              oD("ngIfElse", n),
                (this._elseTemplateRef = n),
                (this._elseViewRef = null),
                this._updateView();
            }
            _updateView() {
              this._context.$implicit
                ? this._thenViewRef ||
                  (this._viewContainer.clear(),
                  (this._elseViewRef = null),
                  this._thenTemplateRef &&
                    (this._thenViewRef = this._viewContainer.createEmbeddedView(
                      this._thenTemplateRef,
                      this._context,
                    )))
                : this._elseViewRef ||
                  (this._viewContainer.clear(),
                  (this._thenViewRef = null),
                  this._elseTemplateRef &&
                    (this._elseViewRef = this._viewContainer.createEmbeddedView(
                      this._elseTemplateRef,
                      this._context,
                    )));
            }
            static ngTemplateContextGuard(n, r) {
              return !0;
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(x(Ut), x(In));
              };
            }
            static {
              this.ɵdir = re({
                type: e,
                selectors: [["", "ngIf", ""]],
                inputs: {
                  ngIf: "ngIf",
                  ngIfThen: "ngIfThen",
                  ngIfElse: "ngIfElse",
                },
                standalone: !0,
              });
            }
          }
          return e;
        })();
      class Lk {
        constructor() {
          (this.$implicit = null), (this.ngIf = null);
        }
      }
      function oD(e, t) {
        if (t && !t.createEmbeddedView)
          throw new Error(
            `${e} must be a TemplateRef, but received '${Ce(t)}'.`,
          );
      }
      let rh = (() => {
        class e {
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵmod = Be({ type: e });
          }
          static {
            this.ɵinj = Ne({});
          }
        }
        return e;
      })();
      const cD = "browser";
      function lD(e) {
        return "server" === e;
      }
      let fF = (() => {
        class e {
          static {
            this.ɵprov = S({
              token: e,
              providedIn: "root",
              factory: () => new hF(D(ce), window),
            });
          }
        }
        return e;
      })();
      class hF {
        constructor(t, n) {
          (this.document = t), (this.window = n), (this.offset = () => [0, 0]);
        }
        setOffset(t) {
          this.offset = Array.isArray(t) ? () => t : t;
        }
        getScrollPosition() {
          return this.supportsScrolling()
            ? [this.window.pageXOffset, this.window.pageYOffset]
            : [0, 0];
        }
        scrollToPosition(t) {
          this.supportsScrolling() && this.window.scrollTo(t[0], t[1]);
        }
        scrollToAnchor(t) {
          if (!this.supportsScrolling()) return;
          const n = (function pF(e, t) {
            const n = e.getElementById(t) || e.getElementsByName(t)[0];
            if (n) return n;
            if (
              "function" == typeof e.createTreeWalker &&
              e.body &&
              "function" == typeof e.body.attachShadow
            ) {
              const r = e.createTreeWalker(e.body, NodeFilter.SHOW_ELEMENT);
              let i = r.currentNode;
              for (; i; ) {
                const o = i.shadowRoot;
                if (o) {
                  const s =
                    o.getElementById(t) || o.querySelector(`[name="${t}"]`);
                  if (s) return s;
                }
                i = r.nextNode();
              }
            }
            return null;
          })(this.document, t);
          n && (this.scrollToElement(n), n.focus());
        }
        setHistoryScrollRestoration(t) {
          this.supportsScrolling() &&
            (this.window.history.scrollRestoration = t);
        }
        scrollToElement(t) {
          const n = t.getBoundingClientRect(),
            r = n.left + this.window.pageXOffset,
            i = n.top + this.window.pageYOffset,
            o = this.offset();
          this.window.scrollTo(r - o[0], i - o[1]);
        }
        supportsScrolling() {
          try {
            return (
              !!this.window &&
              !!this.window.scrollTo &&
              "pageXOffset" in this.window
            );
          } catch {
            return !1;
          }
        }
      }
      class uD {}
      class LF extends zP {
        constructor() {
          super(...arguments), (this.supportsDOMEvents = !0);
        }
      }
      class sh extends LF {
        static makeCurrent() {
          !(function HP(e) {
            Bf || (Bf = e);
          })(new sh());
        }
        onAndCancel(t, n, r) {
          return (
            t.addEventListener(n, r),
            () => {
              t.removeEventListener(n, r);
            }
          );
        }
        dispatchEvent(t, n) {
          t.dispatchEvent(n);
        }
        remove(t) {
          t.parentNode && t.parentNode.removeChild(t);
        }
        createElement(t, n) {
          return (n = n || this.getDefaultDocument()).createElement(t);
        }
        createHtmlDocument() {
          return document.implementation.createHTMLDocument("fakeTitle");
        }
        getDefaultDocument() {
          return document;
        }
        isElementNode(t) {
          return t.nodeType === Node.ELEMENT_NODE;
        }
        isShadowRoot(t) {
          return t instanceof DocumentFragment;
        }
        getGlobalEventTarget(t, n) {
          return "window" === n
            ? window
            : "document" === n
            ? t
            : "body" === n
            ? t.body
            : null;
        }
        getBaseHref(t) {
          const n = (function jF() {
            return (
              (ls = ls || document.querySelector("base")),
              ls ? ls.getAttribute("href") : null
            );
          })();
          return null == n
            ? null
            : (function BF(e) {
                (Rc = Rc || document.createElement("a")),
                  Rc.setAttribute("href", e);
                const t = Rc.pathname;
                return "/" === t.charAt(0) ? t : `/${t}`;
              })(n);
        }
        resetBaseElement() {
          ls = null;
        }
        getUserAgent() {
          return window.navigator.userAgent;
        }
        getCookie(t) {
          return J0(document.cookie, t);
        }
      }
      let Rc,
        ls = null,
        $F = (() => {
          class e {
            build() {
              return new XMLHttpRequest();
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac });
            }
          }
          return e;
        })();
      const ah = new E("EventManagerPlugins");
      let mD = (() => {
        class e {
          constructor(n, r) {
            (this._zone = r),
              (this._eventNameToPlugin = new Map()),
              n.forEach((i) => {
                i.manager = this;
              }),
              (this._plugins = n.slice().reverse());
          }
          addEventListener(n, r, i) {
            return this._findPluginFor(r).addEventListener(n, r, i);
          }
          getZone() {
            return this._zone;
          }
          _findPluginFor(n) {
            let r = this._eventNameToPlugin.get(n);
            if (r) return r;
            if (((r = this._plugins.find((o) => o.supports(n))), !r))
              throw new v(5101, !1);
            return this._eventNameToPlugin.set(n, r), r;
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(ah), D(W));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      class gD {
        constructor(t) {
          this._doc = t;
        }
      }
      const ch = "ng-app-id";
      let bD = (() => {
        class e {
          constructor(n, r, i, o = {}) {
            (this.doc = n),
              (this.appId = r),
              (this.nonce = i),
              (this.platformId = o),
              (this.styleRef = new Map()),
              (this.hostNodes = new Set()),
              (this.styleNodesInDOM = this.collectServerRenderedStyles()),
              (this.platformIsServer = lD(o)),
              this.resetHostNodes();
          }
          addStyles(n) {
            for (const r of n)
              1 === this.changeUsageCount(r, 1) && this.onStyleAdded(r);
          }
          removeStyles(n) {
            for (const r of n)
              this.changeUsageCount(r, -1) <= 0 && this.onStyleRemoved(r);
          }
          ngOnDestroy() {
            const n = this.styleNodesInDOM;
            n && (n.forEach((r) => r.remove()), n.clear());
            for (const r of this.getAllStyles()) this.onStyleRemoved(r);
            this.resetHostNodes();
          }
          addHost(n) {
            this.hostNodes.add(n);
            for (const r of this.getAllStyles()) this.addStyleToHost(n, r);
          }
          removeHost(n) {
            this.hostNodes.delete(n);
          }
          getAllStyles() {
            return this.styleRef.keys();
          }
          onStyleAdded(n) {
            for (const r of this.hostNodes) this.addStyleToHost(r, n);
          }
          onStyleRemoved(n) {
            const r = this.styleRef;
            r.get(n)?.elements?.forEach((i) => i.remove()), r.delete(n);
          }
          collectServerRenderedStyles() {
            const n = this.doc.head?.querySelectorAll(
              `style[${ch}="${this.appId}"]`,
            );
            if (n?.length) {
              const r = new Map();
              return (
                n.forEach((i) => {
                  null != i.textContent && r.set(i.textContent, i);
                }),
                r
              );
            }
            return null;
          }
          changeUsageCount(n, r) {
            const i = this.styleRef;
            if (i.has(n)) {
              const o = i.get(n);
              return (o.usage += r), o.usage;
            }
            return i.set(n, { usage: r, elements: [] }), r;
          }
          getStyleElement(n, r) {
            const i = this.styleNodesInDOM,
              o = i?.get(r);
            if (o?.parentNode === n)
              return i.delete(r), o.removeAttribute(ch), o;
            {
              const s = this.doc.createElement("style");
              return (
                this.nonce && s.setAttribute("nonce", this.nonce),
                (s.textContent = r),
                this.platformIsServer && s.setAttribute(ch, this.appId),
                s
              );
            }
          }
          addStyleToHost(n, r) {
            const i = this.getStyleElement(n, r);
            n.appendChild(i);
            const o = this.styleRef,
              s = o.get(r)?.elements;
            s ? s.push(i) : o.set(r, { elements: [i], usage: 1 });
          }
          resetHostNodes() {
            const n = this.hostNodes;
            n.clear(), n.add(this.doc.head);
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(ce), D(Oa), D(ad, 8), D(zn));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      const lh = {
          svg: "http://www.w3.org/2000/svg",
          xhtml: "http://www.w3.org/1999/xhtml",
          xlink: "http://www.w3.org/1999/xlink",
          xml: "http://www.w3.org/XML/1998/namespace",
          xmlns: "http://www.w3.org/2000/xmlns/",
          math: "http://www.w3.org/1998/MathML/",
        },
        uh = /%COMP%/g,
        qF = new E("RemoveStylesOnCompDestroy", {
          providedIn: "root",
          factory: () => !1,
        });
      function vD(e, t) {
        return t.map((n) => n.replace(uh, e));
      }
      let dh = (() => {
        class e {
          constructor(n, r, i, o, s, a, c, l = null) {
            (this.eventManager = n),
              (this.sharedStylesHost = r),
              (this.appId = i),
              (this.removeStylesOnCompDestroy = o),
              (this.doc = s),
              (this.platformId = a),
              (this.ngZone = c),
              (this.nonce = l),
              (this.rendererByCompId = new Map()),
              (this.platformIsServer = lD(a)),
              (this.defaultRenderer = new fh(n, s, c, this.platformIsServer));
          }
          createRenderer(n, r) {
            if (!n || !r) return this.defaultRenderer;
            this.platformIsServer &&
              r.encapsulation === It.ShadowDom &&
              (r = { ...r, encapsulation: It.Emulated });
            const i = this.getOrCreateRenderer(n, r);
            return (
              i instanceof DD
                ? i.applyToHost(n)
                : i instanceof hh && i.applyStyles(),
              i
            );
          }
          getOrCreateRenderer(n, r) {
            const i = this.rendererByCompId;
            let o = i.get(r.id);
            if (!o) {
              const s = this.doc,
                a = this.ngZone,
                c = this.eventManager,
                l = this.sharedStylesHost,
                u = this.removeStylesOnCompDestroy,
                d = this.platformIsServer;
              switch (r.encapsulation) {
                case It.Emulated:
                  o = new DD(c, l, r, this.appId, u, s, a, d);
                  break;
                case It.ShadowDom:
                  return new ZF(c, l, n, r, s, a, this.nonce, d);
                default:
                  o = new hh(c, l, r, u, s, a, d);
              }
              i.set(r.id, o);
            }
            return o;
          }
          ngOnDestroy() {
            this.rendererByCompId.clear();
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(
                D(mD),
                D(bD),
                D(Oa),
                D(qF),
                D(ce),
                D(zn),
                D(W),
                D(ad),
              );
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      class fh {
        constructor(t, n, r, i) {
          (this.eventManager = t),
            (this.doc = n),
            (this.ngZone = r),
            (this.platformIsServer = i),
            (this.data = Object.create(null)),
            (this.destroyNode = null);
        }
        destroy() {}
        createElement(t, n) {
          return n
            ? this.doc.createElementNS(lh[n] || n, t)
            : this.doc.createElement(t);
        }
        createComment(t) {
          return this.doc.createComment(t);
        }
        createText(t) {
          return this.doc.createTextNode(t);
        }
        appendChild(t, n) {
          (_D(t) ? t.content : t).appendChild(n);
        }
        insertBefore(t, n, r) {
          t && (_D(t) ? t.content : t).insertBefore(n, r);
        }
        removeChild(t, n) {
          t && t.removeChild(n);
        }
        selectRootElement(t, n) {
          let r = "string" == typeof t ? this.doc.querySelector(t) : t;
          if (!r) throw new v(-5104, !1);
          return n || (r.textContent = ""), r;
        }
        parentNode(t) {
          return t.parentNode;
        }
        nextSibling(t) {
          return t.nextSibling;
        }
        setAttribute(t, n, r, i) {
          if (i) {
            n = i + ":" + n;
            const o = lh[i];
            o ? t.setAttributeNS(o, n, r) : t.setAttribute(n, r);
          } else t.setAttribute(n, r);
        }
        removeAttribute(t, n, r) {
          if (r) {
            const i = lh[r];
            i ? t.removeAttributeNS(i, n) : t.removeAttribute(`${r}:${n}`);
          } else t.removeAttribute(n);
        }
        addClass(t, n) {
          t.classList.add(n);
        }
        removeClass(t, n) {
          t.classList.remove(n);
        }
        setStyle(t, n, r, i) {
          i & (Hn.DashCase | Hn.Important)
            ? t.style.setProperty(n, r, i & Hn.Important ? "important" : "")
            : (t.style[n] = r);
        }
        removeStyle(t, n, r) {
          r & Hn.DashCase ? t.style.removeProperty(n) : (t.style[n] = "");
        }
        setProperty(t, n, r) {
          t[n] = r;
        }
        setValue(t, n) {
          t.nodeValue = n;
        }
        listen(t, n, r) {
          if (
            "string" == typeof t &&
            !(t = Pi().getGlobalEventTarget(this.doc, t))
          )
            throw new Error(`Unsupported event target ${t} for event ${n}`);
          return this.eventManager.addEventListener(
            t,
            n,
            this.decoratePreventDefault(r),
          );
        }
        decoratePreventDefault(t) {
          return (n) => {
            if ("__ngUnwrap__" === n) return t;
            !1 ===
              (this.platformIsServer
                ? this.ngZone.runGuarded(() => t(n))
                : t(n)) && n.preventDefault();
          };
        }
      }
      function _D(e) {
        return "TEMPLATE" === e.tagName && void 0 !== e.content;
      }
      class ZF extends fh {
        constructor(t, n, r, i, o, s, a, c) {
          super(t, o, s, c),
            (this.sharedStylesHost = n),
            (this.hostEl = r),
            (this.shadowRoot = r.attachShadow({ mode: "open" })),
            this.sharedStylesHost.addHost(this.shadowRoot);
          const l = vD(i.id, i.styles);
          for (const u of l) {
            const d = document.createElement("style");
            a && d.setAttribute("nonce", a),
              (d.textContent = u),
              this.shadowRoot.appendChild(d);
          }
        }
        nodeOrShadowRoot(t) {
          return t === this.hostEl ? this.shadowRoot : t;
        }
        appendChild(t, n) {
          return super.appendChild(this.nodeOrShadowRoot(t), n);
        }
        insertBefore(t, n, r) {
          return super.insertBefore(this.nodeOrShadowRoot(t), n, r);
        }
        removeChild(t, n) {
          return super.removeChild(this.nodeOrShadowRoot(t), n);
        }
        parentNode(t) {
          return this.nodeOrShadowRoot(
            super.parentNode(this.nodeOrShadowRoot(t)),
          );
        }
        destroy() {
          this.sharedStylesHost.removeHost(this.shadowRoot);
        }
      }
      class hh extends fh {
        constructor(t, n, r, i, o, s, a, c) {
          super(t, o, s, a),
            (this.sharedStylesHost = n),
            (this.removeStylesOnCompDestroy = i),
            (this.styles = c ? vD(c, r.styles) : r.styles);
        }
        applyStyles() {
          this.sharedStylesHost.addStyles(this.styles);
        }
        destroy() {
          this.removeStylesOnCompDestroy &&
            this.sharedStylesHost.removeStyles(this.styles);
        }
      }
      class DD extends hh {
        constructor(t, n, r, i, o, s, a, c) {
          const l = i + "-" + r.id;
          super(t, n, r, o, s, a, c, l),
            (this.contentAttr = (function GF(e) {
              return "_ngcontent-%COMP%".replace(uh, e);
            })(l)),
            (this.hostAttr = (function WF(e) {
              return "_nghost-%COMP%".replace(uh, e);
            })(l));
        }
        applyToHost(t) {
          this.applyStyles(), this.setAttribute(t, this.hostAttr, "");
        }
        createElement(t, n) {
          const r = super.createElement(t, n);
          return super.setAttribute(r, this.contentAttr, ""), r;
        }
      }
      let QF = (() => {
        class e extends gD {
          constructor(n) {
            super(n);
          }
          supports(n) {
            return !0;
          }
          addEventListener(n, r, i) {
            return (
              n.addEventListener(r, i, !1),
              () => this.removeEventListener(n, r, i)
            );
          }
          removeEventListener(n, r, i) {
            return n.removeEventListener(r, i);
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(ce));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      const wD = ["alt", "control", "meta", "shift"],
        YF = {
          "\b": "Backspace",
          "\t": "Tab",
          "\x7f": "Delete",
          "\x1b": "Escape",
          Del: "Delete",
          Esc: "Escape",
          Left: "ArrowLeft",
          Right: "ArrowRight",
          Up: "ArrowUp",
          Down: "ArrowDown",
          Menu: "ContextMenu",
          Scroll: "ScrollLock",
          Win: "OS",
        },
        XF = {
          alt: (e) => e.altKey,
          control: (e) => e.ctrlKey,
          meta: (e) => e.metaKey,
          shift: (e) => e.shiftKey,
        };
      let JF = (() => {
        class e extends gD {
          constructor(n) {
            super(n);
          }
          supports(n) {
            return null != e.parseEventName(n);
          }
          addEventListener(n, r, i) {
            const o = e.parseEventName(r),
              s = e.eventCallback(o.fullKey, i, this.manager.getZone());
            return this.manager
              .getZone()
              .runOutsideAngular(() => Pi().onAndCancel(n, o.domEventName, s));
          }
          static parseEventName(n) {
            const r = n.toLowerCase().split("."),
              i = r.shift();
            if (0 === r.length || ("keydown" !== i && "keyup" !== i))
              return null;
            const o = e._normalizeKey(r.pop());
            let s = "",
              a = r.indexOf("code");
            if (
              (a > -1 && (r.splice(a, 1), (s = "code.")),
              wD.forEach((l) => {
                const u = r.indexOf(l);
                u > -1 && (r.splice(u, 1), (s += l + "."));
              }),
              (s += o),
              0 != r.length || 0 === o.length)
            )
              return null;
            const c = {};
            return (c.domEventName = i), (c.fullKey = s), c;
          }
          static matchEventFullKeyCode(n, r) {
            let i = YF[n.key] || n.key,
              o = "";
            return (
              r.indexOf("code.") > -1 && ((i = n.code), (o = "code.")),
              !(null == i || !i) &&
                ((i = i.toLowerCase()),
                " " === i ? (i = "space") : "." === i && (i = "dot"),
                wD.forEach((s) => {
                  s !== i && (0, XF[s])(n) && (o += s + ".");
                }),
                (o += i),
                o === r)
            );
          }
          static eventCallback(n, r, i) {
            return (o) => {
              e.matchEventFullKeyCode(o, n) && i.runGuarded(() => r(o));
            };
          }
          static _normalizeKey(n) {
            return "esc" === n ? "escape" : n;
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(ce));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      const rL = p0(TP, "browser", [
          { provide: zn, useValue: cD },
          {
            provide: wb,
            useValue: function eL() {
              sh.makeCurrent();
            },
            multi: !0,
          },
          {
            provide: ce,
            useFactory: function nL() {
              return (
                (function Ix(e) {
                  Ku = e;
                })(document),
                document
              );
            },
            deps: [],
          },
        ]),
        iL = new E(""),
        ID = [
          {
            provide: pc,
            useClass: class VF {
              addToWindow(t) {
                (oe.getAngularTestability = (r, i = !0) => {
                  const o = t.findTestabilityInTree(r, i);
                  if (null == o) throw new v(5103, !1);
                  return o;
                }),
                  (oe.getAllAngularTestabilities = () =>
                    t.getAllTestabilities()),
                  (oe.getAllAngularRootElements = () => t.getAllRootElements()),
                  oe.frameworkStabilizers || (oe.frameworkStabilizers = []),
                  oe.frameworkStabilizers.push((r) => {
                    const i = oe.getAllAngularTestabilities();
                    let o = i.length,
                      s = !1;
                    const a = function (c) {
                      (s = s || c), o--, 0 == o && r(s);
                    };
                    i.forEach((c) => {
                      c.whenStable(a);
                    });
                  });
              }
              findTestabilityInTree(t, n, r) {
                return null == n
                  ? null
                  : t.getTestability(n) ??
                      (r
                        ? Pi().isShadowRoot(n)
                          ? this.findTestabilityInTree(t, n.host, !0)
                          : this.findTestabilityInTree(t, n.parentElement, !0)
                        : null);
              }
            },
            deps: [],
          },
          { provide: l0, useClass: Mf, deps: [W, Sf, pc] },
          { provide: Mf, useClass: Mf, deps: [W, Sf, pc] },
        ],
        MD = [
          { provide: rd, useValue: "root" },
          {
            provide: xt,
            useFactory: function tL() {
              return new xt();
            },
            deps: [],
          },
          { provide: ah, useClass: QF, multi: !0, deps: [ce, W, zn] },
          { provide: ah, useClass: JF, multi: !0, deps: [ce] },
          dh,
          bD,
          mD,
          { provide: Fo, useExisting: dh },
          { provide: uD, useClass: $F, deps: [] },
          [],
        ];
      let SD = (() => {
          class e {
            constructor(n) {}
            static withServerTransition(n) {
              return {
                ngModule: e,
                providers: [{ provide: Oa, useValue: n.appId }],
              };
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(iL, 12));
              };
            }
            static {
              this.ɵmod = Be({ type: e });
            }
            static {
              this.ɵinj = Ne({ providers: [...MD, ...ID], imports: [rh, AP] });
            }
          }
          return e;
        })(),
        xD = (() => {
          class e {
            constructor(n) {
              this._doc = n;
            }
            getTitle() {
              return this._doc.title;
            }
            setTitle(n) {
              this._doc.title = n || "";
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(ce));
              };
            }
            static {
              this.ɵprov = S({
                token: e,
                factory: function (r) {
                  let i = null;
                  return (
                    (i = r
                      ? new r()
                      : (function sL() {
                          return new xD(D(ce));
                        })()),
                    i
                  );
                },
                providedIn: "root",
              });
            }
          }
          return e;
        })();
      typeof window < "u" && window;
      let mh = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵprov = S({
                token: e,
                factory: function (r) {
                  let i = null;
                  return (i = r ? new (r || e)() : D(ND)), i;
                },
                providedIn: "root",
              });
            }
          }
          return e;
        })(),
        ND = (() => {
          class e extends mh {
            constructor(n) {
              super(), (this._doc = n);
            }
            sanitize(n, r) {
              if (null == r) return null;
              switch (n) {
                case Fe.NONE:
                  return r;
                case Fe.HTML:
                  return nn(r, "HTML")
                    ? pt(r)
                    : db(this._doc, String(r)).toString();
                case Fe.STYLE:
                  return nn(r, "Style") ? pt(r) : r;
                case Fe.SCRIPT:
                  if (nn(r, "Script")) return pt(r);
                  throw new v(5200, !1);
                case Fe.URL:
                  return nn(r, "URL") ? pt(r) : xa(String(r));
                case Fe.RESOURCE_URL:
                  if (nn(r, "ResourceURL")) return pt(r);
                  throw new v(5201, !1);
                default:
                  throw new v(5202, !1);
              }
            }
            bypassSecurityTrustHtml(n) {
              return (function Rx(e) {
                return new Mx(e);
              })(n);
            }
            bypassSecurityTrustStyle(n) {
              return (function Ox(e) {
                return new Sx(e);
              })(n);
            }
            bypassSecurityTrustScript(n) {
              return (function Px(e) {
                return new xx(e);
              })(n);
            }
            bypassSecurityTrustUrl(n) {
              return (function kx(e) {
                return new Tx(e);
              })(n);
            }
            bypassSecurityTrustResourceUrl(n) {
              return (function Fx(e) {
                return new Ax(e);
              })(n);
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(ce));
              };
            }
            static {
              this.ɵprov = S({
                token: e,
                factory: function (r) {
                  let i = null;
                  return (
                    (i = r
                      ? new r()
                      : (function uL(e) {
                          return new ND(e.get(ce));
                        })(D(bt))),
                    i
                  );
                },
                providedIn: "root",
              });
            }
          }
          return e;
        })();
      class OD {}
      class dL {}
      const Tn = "*";
      function PD(e, t = null) {
        return { type: 2, steps: e, options: t };
      }
      function kD(e) {
        return { type: 6, styles: e, offset: null };
      }
      class us {
        constructor(t = 0, n = 0) {
          (this._onDoneFns = []),
            (this._onStartFns = []),
            (this._onDestroyFns = []),
            (this._originalOnDoneFns = []),
            (this._originalOnStartFns = []),
            (this._started = !1),
            (this._destroyed = !1),
            (this._finished = !1),
            (this._position = 0),
            (this.parentPlayer = null),
            (this.totalTime = t + n);
        }
        _onFinish() {
          this._finished ||
            ((this._finished = !0),
            this._onDoneFns.forEach((t) => t()),
            (this._onDoneFns = []));
        }
        onStart(t) {
          this._originalOnStartFns.push(t), this._onStartFns.push(t);
        }
        onDone(t) {
          this._originalOnDoneFns.push(t), this._onDoneFns.push(t);
        }
        onDestroy(t) {
          this._onDestroyFns.push(t);
        }
        hasStarted() {
          return this._started;
        }
        init() {}
        play() {
          this.hasStarted() || (this._onStart(), this.triggerMicrotask()),
            (this._started = !0);
        }
        triggerMicrotask() {
          queueMicrotask(() => this._onFinish());
        }
        _onStart() {
          this._onStartFns.forEach((t) => t()), (this._onStartFns = []);
        }
        pause() {}
        restart() {}
        finish() {
          this._onFinish();
        }
        destroy() {
          this._destroyed ||
            ((this._destroyed = !0),
            this.hasStarted() || this._onStart(),
            this.finish(),
            this._onDestroyFns.forEach((t) => t()),
            (this._onDestroyFns = []));
        }
        reset() {
          (this._started = !1),
            (this._finished = !1),
            (this._onStartFns = this._originalOnStartFns),
            (this._onDoneFns = this._originalOnDoneFns);
        }
        setPosition(t) {
          this._position = this.totalTime ? t * this.totalTime : 1;
        }
        getPosition() {
          return this.totalTime ? this._position / this.totalTime : 1;
        }
        triggerCallback(t) {
          const n = "start" == t ? this._onStartFns : this._onDoneFns;
          n.forEach((r) => r()), (n.length = 0);
        }
      }
      class FD {
        constructor(t) {
          (this._onDoneFns = []),
            (this._onStartFns = []),
            (this._finished = !1),
            (this._started = !1),
            (this._destroyed = !1),
            (this._onDestroyFns = []),
            (this.parentPlayer = null),
            (this.totalTime = 0),
            (this.players = t);
          let n = 0,
            r = 0,
            i = 0;
          const o = this.players.length;
          0 == o
            ? queueMicrotask(() => this._onFinish())
            : this.players.forEach((s) => {
                s.onDone(() => {
                  ++n == o && this._onFinish();
                }),
                  s.onDestroy(() => {
                    ++r == o && this._onDestroy();
                  }),
                  s.onStart(() => {
                    ++i == o && this._onStart();
                  });
              }),
            (this.totalTime = this.players.reduce(
              (s, a) => Math.max(s, a.totalTime),
              0,
            ));
        }
        _onFinish() {
          this._finished ||
            ((this._finished = !0),
            this._onDoneFns.forEach((t) => t()),
            (this._onDoneFns = []));
        }
        init() {
          this.players.forEach((t) => t.init());
        }
        onStart(t) {
          this._onStartFns.push(t);
        }
        _onStart() {
          this.hasStarted() ||
            ((this._started = !0),
            this._onStartFns.forEach((t) => t()),
            (this._onStartFns = []));
        }
        onDone(t) {
          this._onDoneFns.push(t);
        }
        onDestroy(t) {
          this._onDestroyFns.push(t);
        }
        hasStarted() {
          return this._started;
        }
        play() {
          this.parentPlayer || this.init(),
            this._onStart(),
            this.players.forEach((t) => t.play());
        }
        pause() {
          this.players.forEach((t) => t.pause());
        }
        restart() {
          this.players.forEach((t) => t.restart());
        }
        finish() {
          this._onFinish(), this.players.forEach((t) => t.finish());
        }
        destroy() {
          this._onDestroy();
        }
        _onDestroy() {
          this._destroyed ||
            ((this._destroyed = !0),
            this._onFinish(),
            this.players.forEach((t) => t.destroy()),
            this._onDestroyFns.forEach((t) => t()),
            (this._onDestroyFns = []));
        }
        reset() {
          this.players.forEach((t) => t.reset()),
            (this._destroyed = !1),
            (this._finished = !1),
            (this._started = !1);
        }
        setPosition(t) {
          const n = t * this.totalTime;
          this.players.forEach((r) => {
            const i = r.totalTime ? Math.min(1, n / r.totalTime) : 1;
            r.setPosition(i);
          });
        }
        getPosition() {
          const t = this.players.reduce(
            (n, r) => (null === n || r.totalTime > n.totalTime ? r : n),
            null,
          );
          return null != t ? t.getPosition() : 0;
        }
        beforeDestroy() {
          this.players.forEach((t) => {
            t.beforeDestroy && t.beforeDestroy();
          });
        }
        triggerCallback(t) {
          const n = "start" == t ? this._onStartFns : this._onDoneFns;
          n.forEach((r) => r()), (n.length = 0);
        }
      }
      function LD(e) {
        return new v(3e3, !1);
      }
      function Zn(e) {
        switch (e.length) {
          case 0:
            return new us();
          case 1:
            return e[0];
          default:
            return new FD(e);
        }
      }
      function jD(e, t, n = new Map(), r = new Map()) {
        const i = [],
          o = [];
        let s = -1,
          a = null;
        if (
          (t.forEach((c) => {
            const l = c.get("offset"),
              u = l == s,
              d = (u && a) || new Map();
            c.forEach((f, h) => {
              let p = h,
                m = f;
              if ("offset" !== h)
                switch (((p = e.normalizePropertyName(p, i)), m)) {
                  case "!":
                    m = n.get(h);
                    break;
                  case Tn:
                    m = r.get(h);
                    break;
                  default:
                    m = e.normalizeStyleValue(h, p, m, i);
                }
              d.set(p, m);
            }),
              u || o.push(d),
              (a = d),
              (s = l);
          }),
          i.length)
        )
          throw (function PL(e) {
            return new v(3502, !1);
          })();
        return o;
      }
      function bh(e, t, n, r) {
        switch (t) {
          case "start":
            e.onStart(() => r(n && yh(n, "start", e)));
            break;
          case "done":
            e.onDone(() => r(n && yh(n, "done", e)));
            break;
          case "destroy":
            e.onDestroy(() => r(n && yh(n, "destroy", e)));
        }
      }
      function yh(e, t, n) {
        const o = vh(
            e.element,
            e.triggerName,
            e.fromState,
            e.toState,
            t || e.phaseName,
            n.totalTime ?? e.totalTime,
            !!n.disabled,
          ),
          s = e._data;
        return null != s && (o._data = s), o;
      }
      function vh(e, t, n, r, i = "", o = 0, s) {
        return {
          element: e,
          triggerName: t,
          fromState: n,
          toState: r,
          phaseName: i,
          totalTime: o,
          disabled: !!s,
        };
      }
      function _t(e, t, n) {
        let r = e.get(t);
        return r || e.set(t, (r = n)), r;
      }
      function BD(e) {
        const t = e.indexOf(":");
        return [e.substring(1, t), e.slice(t + 1)];
      }
      const GL = (() =>
        typeof document > "u" ? null : document.documentElement)();
      function _h(e) {
        const t = e.parentNode || e.host || null;
        return t === GL ? null : t;
      }
      let Er = null,
        VD = !1;
      function $D(e, t) {
        for (; t; ) {
          if (t === e) return !0;
          t = _h(t);
        }
        return !1;
      }
      function UD(e, t, n) {
        if (n) return Array.from(e.querySelectorAll(t));
        const r = e.querySelector(t);
        return r ? [r] : [];
      }
      let HD = (() => {
          class e {
            validateStyleProperty(n) {
              return (function KL(e) {
                Er ||
                  ((Er =
                    (function ZL() {
                      return typeof document < "u" ? document.body : null;
                    })() || {}),
                  (VD = !!Er.style && "WebkitAppearance" in Er.style));
                let t = !0;
                return (
                  Er.style &&
                    !(function WL(e) {
                      return "ebkit" == e.substring(1, 6);
                    })(e) &&
                    ((t = e in Er.style),
                    !t &&
                      VD &&
                      (t =
                        "Webkit" + e.charAt(0).toUpperCase() + e.slice(1) in
                        Er.style)),
                  t
                );
              })(n);
            }
            matchesElement(n, r) {
              return !1;
            }
            containsElement(n, r) {
              return $D(n, r);
            }
            getParentElement(n) {
              return _h(n);
            }
            query(n, r, i) {
              return UD(n, r, i);
            }
            computeStyle(n, r, i) {
              return i || "";
            }
            animate(n, r, i, o, s, a = [], c) {
              return new us(i, o);
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac });
            }
          }
          return e;
        })(),
        Dh = (() => {
          class e {
            static {
              this.NOOP = new HD();
            }
          }
          return e;
        })();
      const QL = 1e3,
        wh = "ng-enter",
        Oc = "ng-leave",
        Pc = "ng-trigger",
        kc = ".ng-trigger",
        qD = "ng-animating",
        Eh = ".ng-animating";
      function An(e) {
        if ("number" == typeof e) return e;
        const t = e.match(/^(-?[\.\d]+)(m?s)/);
        return !t || t.length < 2 ? 0 : Ch(parseFloat(t[1]), t[2]);
      }
      function Ch(e, t) {
        return "s" === t ? e * QL : e;
      }
      function Fc(e, t, n) {
        return e.hasOwnProperty("duration")
          ? e
          : (function XL(e, t, n) {
              let i,
                o = 0,
                s = "";
              if ("string" == typeof e) {
                const a = e.match(
                  /^(-?[\.\d]+)(m?s)(?:\s+(-?[\.\d]+)(m?s))?(?:\s+([-a-z]+(?:\(.+?\))?))?$/i,
                );
                if (null === a)
                  return t.push(LD()), { duration: 0, delay: 0, easing: "" };
                i = Ch(parseFloat(a[1]), a[2]);
                const c = a[3];
                null != c && (o = Ch(parseFloat(c), a[4]));
                const l = a[5];
                l && (s = l);
              } else i = e;
              if (!n) {
                let a = !1,
                  c = t.length;
                i < 0 &&
                  (t.push(
                    (function fL() {
                      return new v(3100, !1);
                    })(),
                  ),
                  (a = !0)),
                  o < 0 &&
                    (t.push(
                      (function hL() {
                        return new v(3101, !1);
                      })(),
                    ),
                    (a = !0)),
                  a && t.splice(c, 0, LD());
              }
              return { duration: i, delay: o, easing: s };
            })(e, t, n);
      }
      function ds(e, t = {}) {
        return (
          Object.keys(e).forEach((n) => {
            t[n] = e[n];
          }),
          t
        );
      }
      function GD(e) {
        const t = new Map();
        return (
          Object.keys(e).forEach((n) => {
            t.set(n, e[n]);
          }),
          t
        );
      }
      function Qn(e, t = new Map(), n) {
        if (n) for (let [r, i] of n) t.set(r, i);
        for (let [r, i] of e) t.set(r, i);
        return t;
      }
      function ln(e, t, n) {
        t.forEach((r, i) => {
          const o = Mh(i);
          n && !n.has(i) && n.set(i, e.style[o]), (e.style[o] = r);
        });
      }
      function Cr(e, t) {
        t.forEach((n, r) => {
          const i = Mh(r);
          e.style[i] = "";
        });
      }
      function fs(e) {
        return Array.isArray(e) ? (1 == e.length ? e[0] : PD(e)) : e;
      }
      const Ih = new RegExp("{{\\s*(.+?)\\s*}}", "g");
      function KD(e) {
        let t = [];
        if ("string" == typeof e) {
          let n;
          for (; (n = Ih.exec(e)); ) t.push(n[1]);
          Ih.lastIndex = 0;
        }
        return t;
      }
      function hs(e, t, n) {
        const r = e.toString(),
          i = r.replace(Ih, (o, s) => {
            let a = t[s];
            return (
              null == a &&
                (n.push(
                  (function mL(e) {
                    return new v(3003, !1);
                  })(),
                ),
                (a = "")),
              a.toString()
            );
          });
        return i == r ? e : i;
      }
      function Lc(e) {
        const t = [];
        let n = e.next();
        for (; !n.done; ) t.push(n.value), (n = e.next());
        return t;
      }
      const t2 = /-+([a-z0-9])/g;
      function Mh(e) {
        return e.replace(t2, (...t) => t[1].toUpperCase());
      }
      function Dt(e, t, n) {
        switch (t.type) {
          case 7:
            return e.visitTrigger(t, n);
          case 0:
            return e.visitState(t, n);
          case 1:
            return e.visitTransition(t, n);
          case 2:
            return e.visitSequence(t, n);
          case 3:
            return e.visitGroup(t, n);
          case 4:
            return e.visitAnimate(t, n);
          case 5:
            return e.visitKeyframes(t, n);
          case 6:
            return e.visitStyle(t, n);
          case 8:
            return e.visitReference(t, n);
          case 9:
            return e.visitAnimateChild(t, n);
          case 10:
            return e.visitAnimateRef(t, n);
          case 11:
            return e.visitQuery(t, n);
          case 12:
            return e.visitStagger(t, n);
          default:
            throw (function gL(e) {
              return new v(3004, !1);
            })();
        }
      }
      function ZD(e, t) {
        return window.getComputedStyle(e)[t];
      }
      const jc = "*";
      function i2(e, t) {
        const n = [];
        return (
          "string" == typeof e
            ? e.split(/\s*,\s*/).forEach((r) =>
                (function o2(e, t, n) {
                  if (":" == e[0]) {
                    const c = (function s2(e, t) {
                      switch (e) {
                        case ":enter":
                          return "void => *";
                        case ":leave":
                          return "* => void";
                        case ":increment":
                          return (n, r) => parseFloat(r) > parseFloat(n);
                        case ":decrement":
                          return (n, r) => parseFloat(r) < parseFloat(n);
                        default:
                          return (
                            t.push(
                              (function AL(e) {
                                return new v(3016, !1);
                              })(),
                            ),
                            "* => *"
                          );
                      }
                    })(e, n);
                    if ("function" == typeof c) return void t.push(c);
                    e = c;
                  }
                  const r = e.match(/^(\*|[-\w]+)\s*(<?[=-]>)\s*(\*|[-\w]+)$/);
                  if (null == r || r.length < 4)
                    return (
                      n.push(
                        (function TL(e) {
                          return new v(3015, !1);
                        })(),
                      ),
                      t
                    );
                  const i = r[1],
                    o = r[2],
                    s = r[3];
                  t.push(QD(i, s));
                  "<" == o[0] && !(i == jc && s == jc) && t.push(QD(s, i));
                })(r, n, t),
              )
            : n.push(e),
          n
        );
      }
      const Bc = new Set(["true", "1"]),
        Vc = new Set(["false", "0"]);
      function QD(e, t) {
        const n = Bc.has(e) || Vc.has(e),
          r = Bc.has(t) || Vc.has(t);
        return (i, o) => {
          let s = e == jc || e == i,
            a = t == jc || t == o;
          return (
            !s && n && "boolean" == typeof i && (s = i ? Bc.has(e) : Vc.has(e)),
            !a && r && "boolean" == typeof o && (a = o ? Bc.has(t) : Vc.has(t)),
            s && a
          );
        };
      }
      const a2 = new RegExp("s*:selfs*,?", "g");
      function Sh(e, t, n, r) {
        return new c2(e).build(t, n, r);
      }
      class c2 {
        constructor(t) {
          this._driver = t;
        }
        build(t, n, r) {
          const i = new d2(n);
          return this._resetContextStyleTimingState(i), Dt(this, fs(t), i);
        }
        _resetContextStyleTimingState(t) {
          (t.currentQuerySelector = ""),
            (t.collectedStyles = new Map()),
            t.collectedStyles.set("", new Map()),
            (t.currentTime = 0);
        }
        visitTrigger(t, n) {
          let r = (n.queryCount = 0),
            i = (n.depCount = 0);
          const o = [],
            s = [];
          return (
            "@" == t.name.charAt(0) &&
              n.errors.push(
                (function yL() {
                  return new v(3006, !1);
                })(),
              ),
            t.definitions.forEach((a) => {
              if ((this._resetContextStyleTimingState(n), 0 == a.type)) {
                const c = a,
                  l = c.name;
                l
                  .toString()
                  .split(/\s*,\s*/)
                  .forEach((u) => {
                    (c.name = u), o.push(this.visitState(c, n));
                  }),
                  (c.name = l);
              } else if (1 == a.type) {
                const c = this.visitTransition(a, n);
                (r += c.queryCount), (i += c.depCount), s.push(c);
              } else
                n.errors.push(
                  (function vL() {
                    return new v(3007, !1);
                  })(),
                );
            }),
            {
              type: 7,
              name: t.name,
              states: o,
              transitions: s,
              queryCount: r,
              depCount: i,
              options: null,
            }
          );
        }
        visitState(t, n) {
          const r = this.visitStyle(t.styles, n),
            i = (t.options && t.options.params) || null;
          if (r.containsDynamicStyles) {
            const o = new Set(),
              s = i || {};
            r.styles.forEach((a) => {
              a instanceof Map &&
                a.forEach((c) => {
                  KD(c).forEach((l) => {
                    s.hasOwnProperty(l) || o.add(l);
                  });
                });
            }),
              o.size &&
                (Lc(o.values()),
                n.errors.push(
                  (function _L(e, t) {
                    return new v(3008, !1);
                  })(),
                ));
          }
          return {
            type: 0,
            name: t.name,
            style: r,
            options: i ? { params: i } : null,
          };
        }
        visitTransition(t, n) {
          (n.queryCount = 0), (n.depCount = 0);
          const r = Dt(this, fs(t.animation), n);
          return {
            type: 1,
            matchers: i2(t.expr, n.errors),
            animation: r,
            queryCount: n.queryCount,
            depCount: n.depCount,
            options: Ir(t.options),
          };
        }
        visitSequence(t, n) {
          return {
            type: 2,
            steps: t.steps.map((r) => Dt(this, r, n)),
            options: Ir(t.options),
          };
        }
        visitGroup(t, n) {
          const r = n.currentTime;
          let i = 0;
          const o = t.steps.map((s) => {
            n.currentTime = r;
            const a = Dt(this, s, n);
            return (i = Math.max(i, n.currentTime)), a;
          });
          return (
            (n.currentTime = i), { type: 3, steps: o, options: Ir(t.options) }
          );
        }
        visitAnimate(t, n) {
          const r = (function h2(e, t) {
            if (e.hasOwnProperty("duration")) return e;
            if ("number" == typeof e) return xh(Fc(e, t).duration, 0, "");
            const n = e;
            if (
              n
                .split(/\s+/)
                .some((o) => "{" == o.charAt(0) && "{" == o.charAt(1))
            ) {
              const o = xh(0, 0, "");
              return (o.dynamic = !0), (o.strValue = n), o;
            }
            const i = Fc(n, t);
            return xh(i.duration, i.delay, i.easing);
          })(t.timings, n.errors);
          n.currentAnimateTimings = r;
          let i,
            o = t.styles ? t.styles : kD({});
          if (5 == o.type) i = this.visitKeyframes(o, n);
          else {
            let s = t.styles,
              a = !1;
            if (!s) {
              a = !0;
              const l = {};
              r.easing && (l.easing = r.easing), (s = kD(l));
            }
            n.currentTime += r.duration + r.delay;
            const c = this.visitStyle(s, n);
            (c.isEmptyStep = a), (i = c);
          }
          return (
            (n.currentAnimateTimings = null),
            { type: 4, timings: r, style: i, options: null }
          );
        }
        visitStyle(t, n) {
          const r = this._makeStyleAst(t, n);
          return this._validateStyleAst(r, n), r;
        }
        _makeStyleAst(t, n) {
          const r = [],
            i = Array.isArray(t.styles) ? t.styles : [t.styles];
          for (let a of i)
            "string" == typeof a
              ? a === Tn
                ? r.push(a)
                : n.errors.push(new v(3002, !1))
              : r.push(GD(a));
          let o = !1,
            s = null;
          return (
            r.forEach((a) => {
              if (
                a instanceof Map &&
                (a.has("easing") && ((s = a.get("easing")), a.delete("easing")),
                !o)
              )
                for (let c of a.values())
                  if (c.toString().indexOf("{{") >= 0) {
                    o = !0;
                    break;
                  }
            }),
            {
              type: 6,
              styles: r,
              easing: s,
              offset: t.offset,
              containsDynamicStyles: o,
              options: null,
            }
          );
        }
        _validateStyleAst(t, n) {
          const r = n.currentAnimateTimings;
          let i = n.currentTime,
            o = n.currentTime;
          r && o > 0 && (o -= r.duration + r.delay),
            t.styles.forEach((s) => {
              "string" != typeof s &&
                s.forEach((a, c) => {
                  const l = n.collectedStyles.get(n.currentQuerySelector),
                    u = l.get(c);
                  let d = !0;
                  u &&
                    (o != i &&
                      o >= u.startTime &&
                      i <= u.endTime &&
                      (n.errors.push(
                        (function wL(e, t, n, r, i) {
                          return new v(3010, !1);
                        })(),
                      ),
                      (d = !1)),
                    (o = u.startTime)),
                    d && l.set(c, { startTime: o, endTime: i }),
                    n.options &&
                      (function e2(e, t, n) {
                        const r = t.params || {},
                          i = KD(e);
                        i.length &&
                          i.forEach((o) => {
                            r.hasOwnProperty(o) ||
                              n.push(
                                (function pL(e) {
                                  return new v(3001, !1);
                                })(),
                              );
                          });
                      })(a, n.options, n.errors);
                });
            });
        }
        visitKeyframes(t, n) {
          const r = { type: 5, styles: [], options: null };
          if (!n.currentAnimateTimings)
            return (
              n.errors.push(
                (function EL() {
                  return new v(3011, !1);
                })(),
              ),
              r
            );
          let o = 0;
          const s = [];
          let a = !1,
            c = !1,
            l = 0;
          const u = t.steps.map((y) => {
            const b = this._makeStyleAst(y, n);
            let w =
                null != b.offset
                  ? b.offset
                  : (function f2(e) {
                      if ("string" == typeof e) return null;
                      let t = null;
                      if (Array.isArray(e))
                        e.forEach((n) => {
                          if (n instanceof Map && n.has("offset")) {
                            const r = n;
                            (t = parseFloat(r.get("offset"))),
                              r.delete("offset");
                          }
                        });
                      else if (e instanceof Map && e.has("offset")) {
                        const n = e;
                        (t = parseFloat(n.get("offset"))), n.delete("offset");
                      }
                      return t;
                    })(b.styles),
              M = 0;
            return (
              null != w && (o++, (M = b.offset = w)),
              (c = c || M < 0 || M > 1),
              (a = a || M < l),
              (l = M),
              s.push(M),
              b
            );
          });
          c &&
            n.errors.push(
              (function CL() {
                return new v(3012, !1);
              })(),
            ),
            a &&
              n.errors.push(
                (function IL() {
                  return new v(3200, !1);
                })(),
              );
          const d = t.steps.length;
          let f = 0;
          o > 0 && o < d
            ? n.errors.push(
                (function ML() {
                  return new v(3202, !1);
                })(),
              )
            : 0 == o && (f = 1 / (d - 1));
          const h = d - 1,
            p = n.currentTime,
            m = n.currentAnimateTimings,
            g = m.duration;
          return (
            u.forEach((y, b) => {
              const w = f > 0 ? (b == h ? 1 : f * b) : s[b],
                M = w * g;
              (n.currentTime = p + m.delay + M),
                (m.duration = M),
                this._validateStyleAst(y, n),
                (y.offset = w),
                r.styles.push(y);
            }),
            r
          );
        }
        visitReference(t, n) {
          return {
            type: 8,
            animation: Dt(this, fs(t.animation), n),
            options: Ir(t.options),
          };
        }
        visitAnimateChild(t, n) {
          return n.depCount++, { type: 9, options: Ir(t.options) };
        }
        visitAnimateRef(t, n) {
          return {
            type: 10,
            animation: this.visitReference(t.animation, n),
            options: Ir(t.options),
          };
        }
        visitQuery(t, n) {
          const r = n.currentQuerySelector,
            i = t.options || {};
          n.queryCount++, (n.currentQuery = t);
          const [o, s] = (function l2(e) {
            const t = !!e.split(/\s*,\s*/).find((n) => ":self" == n);
            return (
              t && (e = e.replace(a2, "")),
              (e = e
                .replace(/@\*/g, kc)
                .replace(/@\w+/g, (n) => kc + "-" + n.slice(1))
                .replace(/:animating/g, Eh)),
              [e, t]
            );
          })(t.selector);
          (n.currentQuerySelector = r.length ? r + " " + o : o),
            _t(n.collectedStyles, n.currentQuerySelector, new Map());
          const a = Dt(this, fs(t.animation), n);
          return (
            (n.currentQuery = null),
            (n.currentQuerySelector = r),
            {
              type: 11,
              selector: o,
              limit: i.limit || 0,
              optional: !!i.optional,
              includeSelf: s,
              animation: a,
              originalSelector: t.selector,
              options: Ir(t.options),
            }
          );
        }
        visitStagger(t, n) {
          n.currentQuery ||
            n.errors.push(
              (function SL() {
                return new v(3013, !1);
              })(),
            );
          const r =
            "full" === t.timings
              ? { duration: 0, delay: 0, easing: "full" }
              : Fc(t.timings, n.errors, !0);
          return {
            type: 12,
            animation: Dt(this, fs(t.animation), n),
            timings: r,
            options: null,
          };
        }
      }
      class d2 {
        constructor(t) {
          (this.errors = t),
            (this.queryCount = 0),
            (this.depCount = 0),
            (this.currentTransition = null),
            (this.currentQuery = null),
            (this.currentQuerySelector = null),
            (this.currentAnimateTimings = null),
            (this.currentTime = 0),
            (this.collectedStyles = new Map()),
            (this.options = null),
            (this.unsupportedCSSPropertiesFound = new Set());
        }
      }
      function Ir(e) {
        return (
          e
            ? (e = ds(e)).params &&
              (e.params = (function u2(e) {
                return e ? ds(e) : null;
              })(e.params))
            : (e = {}),
          e
        );
      }
      function xh(e, t, n) {
        return { duration: e, delay: t, easing: n };
      }
      function Th(e, t, n, r, i, o, s = null, a = !1) {
        return {
          type: 1,
          element: e,
          keyframes: t,
          preStyleProps: n,
          postStyleProps: r,
          duration: i,
          delay: o,
          totalTime: i + o,
          easing: s,
          subTimeline: a,
        };
      }
      class $c {
        constructor() {
          this._map = new Map();
        }
        get(t) {
          return this._map.get(t) || [];
        }
        append(t, n) {
          let r = this._map.get(t);
          r || this._map.set(t, (r = [])), r.push(...n);
        }
        has(t) {
          return this._map.has(t);
        }
        clear() {
          this._map.clear();
        }
      }
      const g2 = new RegExp(":enter", "g"),
        y2 = new RegExp(":leave", "g");
      function Ah(e, t, n, r, i, o = new Map(), s = new Map(), a, c, l = []) {
        return new v2().buildKeyframes(e, t, n, r, i, o, s, a, c, l);
      }
      class v2 {
        buildKeyframes(t, n, r, i, o, s, a, c, l, u = []) {
          l = l || new $c();
          const d = new Nh(t, n, l, i, o, u, []);
          d.options = c;
          const f = c.delay ? An(c.delay) : 0;
          d.currentTimeline.delayNextStep(f),
            d.currentTimeline.setStyles([s], null, d.errors, c),
            Dt(this, r, d);
          const h = d.timelines.filter((p) => p.containsAnimation());
          if (h.length && a.size) {
            let p;
            for (let m = h.length - 1; m >= 0; m--) {
              const g = h[m];
              if (g.element === n) {
                p = g;
                break;
              }
            }
            p &&
              !p.allowOnlyTimelineStyles() &&
              p.setStyles([a], null, d.errors, c);
          }
          return h.length
            ? h.map((p) => p.buildKeyframes())
            : [Th(n, [], [], [], 0, f, "", !1)];
        }
        visitTrigger(t, n) {}
        visitState(t, n) {}
        visitTransition(t, n) {}
        visitAnimateChild(t, n) {
          const r = n.subInstructions.get(n.element);
          if (r) {
            const i = n.createSubContext(t.options),
              o = n.currentTimeline.currentTime,
              s = this._visitSubInstructions(r, i, i.options);
            o != s && n.transformIntoNewTimeline(s);
          }
          n.previousNode = t;
        }
        visitAnimateRef(t, n) {
          const r = n.createSubContext(t.options);
          r.transformIntoNewTimeline(),
            this._applyAnimationRefDelays(
              [t.options, t.animation.options],
              n,
              r,
            ),
            this.visitReference(t.animation, r),
            n.transformIntoNewTimeline(r.currentTimeline.currentTime),
            (n.previousNode = t);
        }
        _applyAnimationRefDelays(t, n, r) {
          for (const i of t) {
            const o = i?.delay;
            if (o) {
              const s =
                "number" == typeof o ? o : An(hs(o, i?.params ?? {}, n.errors));
              r.delayNextStep(s);
            }
          }
        }
        _visitSubInstructions(t, n, r) {
          let o = n.currentTimeline.currentTime;
          const s = null != r.duration ? An(r.duration) : null,
            a = null != r.delay ? An(r.delay) : null;
          return (
            0 !== s &&
              t.forEach((c) => {
                const l = n.appendInstructionToTimeline(c, s, a);
                o = Math.max(o, l.duration + l.delay);
              }),
            o
          );
        }
        visitReference(t, n) {
          n.updateOptions(t.options, !0),
            Dt(this, t.animation, n),
            (n.previousNode = t);
        }
        visitSequence(t, n) {
          const r = n.subContextCount;
          let i = n;
          const o = t.options;
          if (
            o &&
            (o.params || o.delay) &&
            ((i = n.createSubContext(o)),
            i.transformIntoNewTimeline(),
            null != o.delay)
          ) {
            6 == i.previousNode.type &&
              (i.currentTimeline.snapshotCurrentStyles(),
              (i.previousNode = Uc));
            const s = An(o.delay);
            i.delayNextStep(s);
          }
          t.steps.length &&
            (t.steps.forEach((s) => Dt(this, s, i)),
            i.currentTimeline.applyStylesToKeyframe(),
            i.subContextCount > r && i.transformIntoNewTimeline()),
            (n.previousNode = t);
        }
        visitGroup(t, n) {
          const r = [];
          let i = n.currentTimeline.currentTime;
          const o = t.options && t.options.delay ? An(t.options.delay) : 0;
          t.steps.forEach((s) => {
            const a = n.createSubContext(t.options);
            o && a.delayNextStep(o),
              Dt(this, s, a),
              (i = Math.max(i, a.currentTimeline.currentTime)),
              r.push(a.currentTimeline);
          }),
            r.forEach((s) => n.currentTimeline.mergeTimelineCollectedStyles(s)),
            n.transformIntoNewTimeline(i),
            (n.previousNode = t);
        }
        _visitTiming(t, n) {
          if (t.dynamic) {
            const r = t.strValue;
            return Fc(n.params ? hs(r, n.params, n.errors) : r, n.errors);
          }
          return { duration: t.duration, delay: t.delay, easing: t.easing };
        }
        visitAnimate(t, n) {
          const r = (n.currentAnimateTimings = this._visitTiming(t.timings, n)),
            i = n.currentTimeline;
          r.delay && (n.incrementTime(r.delay), i.snapshotCurrentStyles());
          const o = t.style;
          5 == o.type
            ? this.visitKeyframes(o, n)
            : (n.incrementTime(r.duration),
              this.visitStyle(o, n),
              i.applyStylesToKeyframe()),
            (n.currentAnimateTimings = null),
            (n.previousNode = t);
        }
        visitStyle(t, n) {
          const r = n.currentTimeline,
            i = n.currentAnimateTimings;
          !i && r.hasCurrentStyleProperties() && r.forwardFrame();
          const o = (i && i.easing) || t.easing;
          t.isEmptyStep
            ? r.applyEmptyStep(o)
            : r.setStyles(t.styles, o, n.errors, n.options),
            (n.previousNode = t);
        }
        visitKeyframes(t, n) {
          const r = n.currentAnimateTimings,
            i = n.currentTimeline.duration,
            o = r.duration,
            a = n.createSubContext().currentTimeline;
          (a.easing = r.easing),
            t.styles.forEach((c) => {
              a.forwardTime((c.offset || 0) * o),
                a.setStyles(c.styles, c.easing, n.errors, n.options),
                a.applyStylesToKeyframe();
            }),
            n.currentTimeline.mergeTimelineCollectedStyles(a),
            n.transformIntoNewTimeline(i + o),
            (n.previousNode = t);
        }
        visitQuery(t, n) {
          const r = n.currentTimeline.currentTime,
            i = t.options || {},
            o = i.delay ? An(i.delay) : 0;
          o &&
            (6 === n.previousNode.type ||
              (0 == r && n.currentTimeline.hasCurrentStyleProperties())) &&
            (n.currentTimeline.snapshotCurrentStyles(), (n.previousNode = Uc));
          let s = r;
          const a = n.invokeQuery(
            t.selector,
            t.originalSelector,
            t.limit,
            t.includeSelf,
            !!i.optional,
            n.errors,
          );
          n.currentQueryTotal = a.length;
          let c = null;
          a.forEach((l, u) => {
            n.currentQueryIndex = u;
            const d = n.createSubContext(t.options, l);
            o && d.delayNextStep(o),
              l === n.element && (c = d.currentTimeline),
              Dt(this, t.animation, d),
              d.currentTimeline.applyStylesToKeyframe(),
              (s = Math.max(s, d.currentTimeline.currentTime));
          }),
            (n.currentQueryIndex = 0),
            (n.currentQueryTotal = 0),
            n.transformIntoNewTimeline(s),
            c &&
              (n.currentTimeline.mergeTimelineCollectedStyles(c),
              n.currentTimeline.snapshotCurrentStyles()),
            (n.previousNode = t);
        }
        visitStagger(t, n) {
          const r = n.parentContext,
            i = n.currentTimeline,
            o = t.timings,
            s = Math.abs(o.duration),
            a = s * (n.currentQueryTotal - 1);
          let c = s * n.currentQueryIndex;
          switch (o.duration < 0 ? "reverse" : o.easing) {
            case "reverse":
              c = a - c;
              break;
            case "full":
              c = r.currentStaggerTime;
          }
          const u = n.currentTimeline;
          c && u.delayNextStep(c);
          const d = u.currentTime;
          Dt(this, t.animation, n),
            (n.previousNode = t),
            (r.currentStaggerTime =
              i.currentTime - d + (i.startTime - r.currentTimeline.startTime));
        }
      }
      const Uc = {};
      class Nh {
        constructor(t, n, r, i, o, s, a, c) {
          (this._driver = t),
            (this.element = n),
            (this.subInstructions = r),
            (this._enterClassName = i),
            (this._leaveClassName = o),
            (this.errors = s),
            (this.timelines = a),
            (this.parentContext = null),
            (this.currentAnimateTimings = null),
            (this.previousNode = Uc),
            (this.subContextCount = 0),
            (this.options = {}),
            (this.currentQueryIndex = 0),
            (this.currentQueryTotal = 0),
            (this.currentStaggerTime = 0),
            (this.currentTimeline = c || new Hc(this._driver, n, 0)),
            a.push(this.currentTimeline);
        }
        get params() {
          return this.options.params;
        }
        updateOptions(t, n) {
          if (!t) return;
          const r = t;
          let i = this.options;
          null != r.duration && (i.duration = An(r.duration)),
            null != r.delay && (i.delay = An(r.delay));
          const o = r.params;
          if (o) {
            let s = i.params;
            s || (s = this.options.params = {}),
              Object.keys(o).forEach((a) => {
                (!n || !s.hasOwnProperty(a)) &&
                  (s[a] = hs(o[a], s, this.errors));
              });
          }
        }
        _copyOptions() {
          const t = {};
          if (this.options) {
            const n = this.options.params;
            if (n) {
              const r = (t.params = {});
              Object.keys(n).forEach((i) => {
                r[i] = n[i];
              });
            }
          }
          return t;
        }
        createSubContext(t = null, n, r) {
          const i = n || this.element,
            o = new Nh(
              this._driver,
              i,
              this.subInstructions,
              this._enterClassName,
              this._leaveClassName,
              this.errors,
              this.timelines,
              this.currentTimeline.fork(i, r || 0),
            );
          return (
            (o.previousNode = this.previousNode),
            (o.currentAnimateTimings = this.currentAnimateTimings),
            (o.options = this._copyOptions()),
            o.updateOptions(t),
            (o.currentQueryIndex = this.currentQueryIndex),
            (o.currentQueryTotal = this.currentQueryTotal),
            (o.parentContext = this),
            this.subContextCount++,
            o
          );
        }
        transformIntoNewTimeline(t) {
          return (
            (this.previousNode = Uc),
            (this.currentTimeline = this.currentTimeline.fork(this.element, t)),
            this.timelines.push(this.currentTimeline),
            this.currentTimeline
          );
        }
        appendInstructionToTimeline(t, n, r) {
          const i = {
              duration: n ?? t.duration,
              delay: this.currentTimeline.currentTime + (r ?? 0) + t.delay,
              easing: "",
            },
            o = new _2(
              this._driver,
              t.element,
              t.keyframes,
              t.preStyleProps,
              t.postStyleProps,
              i,
              t.stretchStartingKeyframe,
            );
          return this.timelines.push(o), i;
        }
        incrementTime(t) {
          this.currentTimeline.forwardTime(this.currentTimeline.duration + t);
        }
        delayNextStep(t) {
          t > 0 && this.currentTimeline.delayNextStep(t);
        }
        invokeQuery(t, n, r, i, o, s) {
          let a = [];
          if ((i && a.push(this.element), t.length > 0)) {
            t = (t = t.replace(g2, "." + this._enterClassName)).replace(
              y2,
              "." + this._leaveClassName,
            );
            let l = this._driver.query(this.element, t, 1 != r);
            0 !== r &&
              (l = r < 0 ? l.slice(l.length + r, l.length) : l.slice(0, r)),
              a.push(...l);
          }
          return (
            !o &&
              0 == a.length &&
              s.push(
                (function xL(e) {
                  return new v(3014, !1);
                })(),
              ),
            a
          );
        }
      }
      class Hc {
        constructor(t, n, r, i) {
          (this._driver = t),
            (this.element = n),
            (this.startTime = r),
            (this._elementTimelineStylesLookup = i),
            (this.duration = 0),
            (this.easing = null),
            (this._previousKeyframe = new Map()),
            (this._currentKeyframe = new Map()),
            (this._keyframes = new Map()),
            (this._styleSummary = new Map()),
            (this._localTimelineStyles = new Map()),
            (this._pendingStyles = new Map()),
            (this._backFill = new Map()),
            (this._currentEmptyStepKeyframe = null),
            this._elementTimelineStylesLookup ||
              (this._elementTimelineStylesLookup = new Map()),
            (this._globalTimelineStyles =
              this._elementTimelineStylesLookup.get(n)),
            this._globalTimelineStyles ||
              ((this._globalTimelineStyles = this._localTimelineStyles),
              this._elementTimelineStylesLookup.set(
                n,
                this._localTimelineStyles,
              )),
            this._loadKeyframe();
        }
        containsAnimation() {
          switch (this._keyframes.size) {
            case 0:
              return !1;
            case 1:
              return this.hasCurrentStyleProperties();
            default:
              return !0;
          }
        }
        hasCurrentStyleProperties() {
          return this._currentKeyframe.size > 0;
        }
        get currentTime() {
          return this.startTime + this.duration;
        }
        delayNextStep(t) {
          const n = 1 === this._keyframes.size && this._pendingStyles.size;
          this.duration || n
            ? (this.forwardTime(this.currentTime + t),
              n && this.snapshotCurrentStyles())
            : (this.startTime += t);
        }
        fork(t, n) {
          return (
            this.applyStylesToKeyframe(),
            new Hc(
              this._driver,
              t,
              n || this.currentTime,
              this._elementTimelineStylesLookup,
            )
          );
        }
        _loadKeyframe() {
          this._currentKeyframe &&
            (this._previousKeyframe = this._currentKeyframe),
            (this._currentKeyframe = this._keyframes.get(this.duration)),
            this._currentKeyframe ||
              ((this._currentKeyframe = new Map()),
              this._keyframes.set(this.duration, this._currentKeyframe));
        }
        forwardFrame() {
          (this.duration += 1), this._loadKeyframe();
        }
        forwardTime(t) {
          this.applyStylesToKeyframe(),
            (this.duration = t),
            this._loadKeyframe();
        }
        _updateStyle(t, n) {
          this._localTimelineStyles.set(t, n),
            this._globalTimelineStyles.set(t, n),
            this._styleSummary.set(t, { time: this.currentTime, value: n });
        }
        allowOnlyTimelineStyles() {
          return this._currentEmptyStepKeyframe !== this._currentKeyframe;
        }
        applyEmptyStep(t) {
          t && this._previousKeyframe.set("easing", t);
          for (let [n, r] of this._globalTimelineStyles)
            this._backFill.set(n, r || Tn), this._currentKeyframe.set(n, Tn);
          this._currentEmptyStepKeyframe = this._currentKeyframe;
        }
        setStyles(t, n, r, i) {
          n && this._previousKeyframe.set("easing", n);
          const o = (i && i.params) || {},
            s = (function D2(e, t) {
              const n = new Map();
              let r;
              return (
                e.forEach((i) => {
                  if ("*" === i) {
                    r = r || t.keys();
                    for (let o of r) n.set(o, Tn);
                  } else Qn(i, n);
                }),
                n
              );
            })(t, this._globalTimelineStyles);
          for (let [a, c] of s) {
            const l = hs(c, o, r);
            this._pendingStyles.set(a, l),
              this._localTimelineStyles.has(a) ||
                this._backFill.set(a, this._globalTimelineStyles.get(a) ?? Tn),
              this._updateStyle(a, l);
          }
        }
        applyStylesToKeyframe() {
          0 != this._pendingStyles.size &&
            (this._pendingStyles.forEach((t, n) => {
              this._currentKeyframe.set(n, t);
            }),
            this._pendingStyles.clear(),
            this._localTimelineStyles.forEach((t, n) => {
              this._currentKeyframe.has(n) || this._currentKeyframe.set(n, t);
            }));
        }
        snapshotCurrentStyles() {
          for (let [t, n] of this._localTimelineStyles)
            this._pendingStyles.set(t, n), this._updateStyle(t, n);
        }
        getFinalKeyframe() {
          return this._keyframes.get(this.duration);
        }
        get properties() {
          const t = [];
          for (let n in this._currentKeyframe) t.push(n);
          return t;
        }
        mergeTimelineCollectedStyles(t) {
          t._styleSummary.forEach((n, r) => {
            const i = this._styleSummary.get(r);
            (!i || n.time > i.time) && this._updateStyle(r, n.value);
          });
        }
        buildKeyframes() {
          this.applyStylesToKeyframe();
          const t = new Set(),
            n = new Set(),
            r = 1 === this._keyframes.size && 0 === this.duration;
          let i = [];
          this._keyframes.forEach((a, c) => {
            const l = Qn(a, new Map(), this._backFill);
            l.forEach((u, d) => {
              "!" === u ? t.add(d) : u === Tn && n.add(d);
            }),
              r || l.set("offset", c / this.duration),
              i.push(l);
          });
          const o = t.size ? Lc(t.values()) : [],
            s = n.size ? Lc(n.values()) : [];
          if (r) {
            const a = i[0],
              c = new Map(a);
            a.set("offset", 0), c.set("offset", 1), (i = [a, c]);
          }
          return Th(
            this.element,
            i,
            o,
            s,
            this.duration,
            this.startTime,
            this.easing,
            !1,
          );
        }
      }
      class _2 extends Hc {
        constructor(t, n, r, i, o, s, a = !1) {
          super(t, n, s.delay),
            (this.keyframes = r),
            (this.preStyleProps = i),
            (this.postStyleProps = o),
            (this._stretchStartingKeyframe = a),
            (this.timings = {
              duration: s.duration,
              delay: s.delay,
              easing: s.easing,
            });
        }
        containsAnimation() {
          return this.keyframes.length > 1;
        }
        buildKeyframes() {
          let t = this.keyframes,
            { delay: n, duration: r, easing: i } = this.timings;
          if (this._stretchStartingKeyframe && n) {
            const o = [],
              s = r + n,
              a = n / s,
              c = Qn(t[0]);
            c.set("offset", 0), o.push(c);
            const l = Qn(t[0]);
            l.set("offset", JD(a)), o.push(l);
            const u = t.length - 1;
            for (let d = 1; d <= u; d++) {
              let f = Qn(t[d]);
              const h = f.get("offset");
              f.set("offset", JD((n + h * r) / s)), o.push(f);
            }
            (r = s), (n = 0), (i = ""), (t = o);
          }
          return Th(
            this.element,
            t,
            this.preStyleProps,
            this.postStyleProps,
            r,
            n,
            i,
            !0,
          );
        }
      }
      function JD(e, t = 3) {
        const n = Math.pow(10, t - 1);
        return Math.round(e * n) / n;
      }
      class Rh {}
      const w2 = new Set([
        "width",
        "height",
        "minWidth",
        "minHeight",
        "maxWidth",
        "maxHeight",
        "left",
        "top",
        "bottom",
        "right",
        "fontSize",
        "outlineWidth",
        "outlineOffset",
        "paddingTop",
        "paddingLeft",
        "paddingBottom",
        "paddingRight",
        "marginTop",
        "marginLeft",
        "marginBottom",
        "marginRight",
        "borderRadius",
        "borderWidth",
        "borderTopWidth",
        "borderLeftWidth",
        "borderRightWidth",
        "borderBottomWidth",
        "textIndent",
        "perspective",
      ]);
      class E2 extends Rh {
        normalizePropertyName(t, n) {
          return Mh(t);
        }
        normalizeStyleValue(t, n, r, i) {
          let o = "";
          const s = r.toString().trim();
          if (w2.has(n) && 0 !== r && "0" !== r)
            if ("number" == typeof r) o = "px";
            else {
              const a = r.match(/^[+-]?[\d\.]+([a-z]*)$/);
              a &&
                0 == a[1].length &&
                i.push(
                  (function bL(e, t) {
                    return new v(3005, !1);
                  })(),
                );
            }
          return s + o;
        }
      }
      function ew(e, t, n, r, i, o, s, a, c, l, u, d, f) {
        return {
          type: 0,
          element: e,
          triggerName: t,
          isRemovalTransition: i,
          fromState: n,
          fromStyles: o,
          toState: r,
          toStyles: s,
          timelines: a,
          queriedElements: c,
          preStyleProps: l,
          postStyleProps: u,
          totalTime: d,
          errors: f,
        };
      }
      const Oh = {};
      class tw {
        constructor(t, n, r) {
          (this._triggerName = t), (this.ast = n), (this._stateStyles = r);
        }
        match(t, n, r, i) {
          return (function C2(e, t, n, r, i) {
            return e.some((o) => o(t, n, r, i));
          })(this.ast.matchers, t, n, r, i);
        }
        buildStyles(t, n, r) {
          let i = this._stateStyles.get("*");
          return (
            void 0 !== t && (i = this._stateStyles.get(t?.toString()) || i),
            i ? i.buildStyles(n, r) : new Map()
          );
        }
        build(t, n, r, i, o, s, a, c, l, u) {
          const d = [],
            f = (this.ast.options && this.ast.options.params) || Oh,
            p = this.buildStyles(r, (a && a.params) || Oh, d),
            m = (c && c.params) || Oh,
            g = this.buildStyles(i, m, d),
            y = new Set(),
            b = new Map(),
            w = new Map(),
            M = "void" === i,
            F = { params: I2(m, f), delay: this.ast.options?.delay },
            te = u ? [] : Ah(t, n, this.ast.animation, o, s, p, g, F, l, d);
          let ue = 0;
          if (
            (te.forEach((wt) => {
              ue = Math.max(wt.duration + wt.delay, ue);
            }),
            d.length)
          )
            return ew(n, this._triggerName, r, i, M, p, g, [], [], b, w, ue, d);
          te.forEach((wt) => {
            const Kt = wt.element,
              Sl = _t(b, Kt, new Set());
            wt.preStyleProps.forEach((Pr) => Sl.add(Pr));
            const js = _t(w, Kt, new Set());
            wt.postStyleProps.forEach((Pr) => js.add(Pr)),
              Kt !== n && y.add(Kt);
          });
          const Le = Lc(y.values());
          return ew(n, this._triggerName, r, i, M, p, g, te, Le, b, w, ue);
        }
      }
      function I2(e, t) {
        const n = ds(t);
        for (const r in e) e.hasOwnProperty(r) && null != e[r] && (n[r] = e[r]);
        return n;
      }
      class M2 {
        constructor(t, n, r) {
          (this.styles = t), (this.defaultParams = n), (this.normalizer = r);
        }
        buildStyles(t, n) {
          const r = new Map(),
            i = ds(this.defaultParams);
          return (
            Object.keys(t).forEach((o) => {
              const s = t[o];
              null !== s && (i[o] = s);
            }),
            this.styles.styles.forEach((o) => {
              "string" != typeof o &&
                o.forEach((s, a) => {
                  s && (s = hs(s, i, n));
                  const c = this.normalizer.normalizePropertyName(a, n);
                  (s = this.normalizer.normalizeStyleValue(a, c, s, n)),
                    r.set(a, s);
                });
            }),
            r
          );
        }
      }
      class x2 {
        constructor(t, n, r) {
          (this.name = t),
            (this.ast = n),
            (this._normalizer = r),
            (this.transitionFactories = []),
            (this.states = new Map()),
            n.states.forEach((i) => {
              this.states.set(
                i.name,
                new M2(i.style, (i.options && i.options.params) || {}, r),
              );
            }),
            nw(this.states, "true", "1"),
            nw(this.states, "false", "0"),
            n.transitions.forEach((i) => {
              this.transitionFactories.push(new tw(t, i, this.states));
            }),
            (this.fallbackTransition = (function T2(e, t, n) {
              return new tw(
                e,
                {
                  type: 1,
                  animation: { type: 2, steps: [], options: null },
                  matchers: [(s, a) => !0],
                  options: null,
                  queryCount: 0,
                  depCount: 0,
                },
                t,
              );
            })(t, this.states));
        }
        get containsQueries() {
          return this.ast.queryCount > 0;
        }
        matchTransition(t, n, r, i) {
          return (
            this.transitionFactories.find((s) => s.match(t, n, r, i)) || null
          );
        }
        matchStyles(t, n, r) {
          return this.fallbackTransition.buildStyles(t, n, r);
        }
      }
      function nw(e, t, n) {
        e.has(t)
          ? e.has(n) || e.set(n, e.get(t))
          : e.has(n) && e.set(t, e.get(n));
      }
      const A2 = new $c();
      class N2 {
        constructor(t, n, r) {
          (this.bodyNode = t),
            (this._driver = n),
            (this._normalizer = r),
            (this._animations = new Map()),
            (this._playersById = new Map()),
            (this.players = []);
        }
        register(t, n) {
          const r = [],
            o = Sh(this._driver, n, r, []);
          if (r.length)
            throw (function kL(e) {
              return new v(3503, !1);
            })();
          this._animations.set(t, o);
        }
        _buildPlayer(t, n, r) {
          const i = t.element,
            o = jD(this._normalizer, t.keyframes, n, r);
          return this._driver.animate(
            i,
            o,
            t.duration,
            t.delay,
            t.easing,
            [],
            !0,
          );
        }
        create(t, n, r = {}) {
          const i = [],
            o = this._animations.get(t);
          let s;
          const a = new Map();
          if (
            (o
              ? ((s = Ah(
                  this._driver,
                  n,
                  o,
                  wh,
                  Oc,
                  new Map(),
                  new Map(),
                  r,
                  A2,
                  i,
                )),
                s.forEach((u) => {
                  const d = _t(a, u.element, new Map());
                  u.postStyleProps.forEach((f) => d.set(f, null));
                }))
              : (i.push(
                  (function FL() {
                    return new v(3300, !1);
                  })(),
                ),
                (s = [])),
            i.length)
          )
            throw (function LL(e) {
              return new v(3504, !1);
            })();
          a.forEach((u, d) => {
            u.forEach((f, h) => {
              u.set(h, this._driver.computeStyle(d, h, Tn));
            });
          });
          const l = Zn(
            s.map((u) => {
              const d = a.get(u.element);
              return this._buildPlayer(u, new Map(), d);
            }),
          );
          return (
            this._playersById.set(t, l),
            l.onDestroy(() => this.destroy(t)),
            this.players.push(l),
            l
          );
        }
        destroy(t) {
          const n = this._getPlayer(t);
          n.destroy(), this._playersById.delete(t);
          const r = this.players.indexOf(n);
          r >= 0 && this.players.splice(r, 1);
        }
        _getPlayer(t) {
          const n = this._playersById.get(t);
          if (!n)
            throw (function jL(e) {
              return new v(3301, !1);
            })();
          return n;
        }
        listen(t, n, r, i) {
          const o = vh(n, "", "", "");
          return bh(this._getPlayer(t), r, o, i), () => {};
        }
        command(t, n, r, i) {
          if ("register" == r) return void this.register(t, i[0]);
          if ("create" == r) return void this.create(t, n, i[0] || {});
          const o = this._getPlayer(t);
          switch (r) {
            case "play":
              o.play();
              break;
            case "pause":
              o.pause();
              break;
            case "reset":
              o.reset();
              break;
            case "restart":
              o.restart();
              break;
            case "finish":
              o.finish();
              break;
            case "init":
              o.init();
              break;
            case "setPosition":
              o.setPosition(parseFloat(i[0]));
              break;
            case "destroy":
              this.destroy(t);
          }
        }
      }
      const rw = "ng-animate-queued",
        Ph = "ng-animate-disabled",
        F2 = [],
        iw = {
          namespaceId: "",
          setForRemoval: !1,
          setForMove: !1,
          hasAnimation: !1,
          removedBeforeQueried: !1,
        },
        L2 = {
          namespaceId: "",
          setForMove: !1,
          setForRemoval: !1,
          hasAnimation: !1,
          removedBeforeQueried: !0,
        },
        qt = "__ng_removed";
      class kh {
        get params() {
          return this.options.params;
        }
        constructor(t, n = "") {
          this.namespaceId = n;
          const r = t && t.hasOwnProperty("value");
          if (
            ((this.value = (function $2(e) {
              return e ?? null;
            })(r ? t.value : t)),
            r)
          ) {
            const o = ds(t);
            delete o.value, (this.options = o);
          } else this.options = {};
          this.options.params || (this.options.params = {});
        }
        absorbOptions(t) {
          const n = t.params;
          if (n) {
            const r = this.options.params;
            Object.keys(n).forEach((i) => {
              null == r[i] && (r[i] = n[i]);
            });
          }
        }
      }
      const ps = "void",
        Fh = new kh(ps);
      class j2 {
        constructor(t, n, r) {
          (this.id = t),
            (this.hostElement = n),
            (this._engine = r),
            (this.players = []),
            (this._triggers = new Map()),
            (this._queue = []),
            (this._elementListeners = new Map()),
            (this._hostClassName = "ng-tns-" + t),
            Ot(n, this._hostClassName);
        }
        listen(t, n, r, i) {
          if (!this._triggers.has(n))
            throw (function BL(e, t) {
              return new v(3302, !1);
            })();
          if (null == r || 0 == r.length)
            throw (function VL(e) {
              return new v(3303, !1);
            })();
          if (
            !(function U2(e) {
              return "start" == e || "done" == e;
            })(r)
          )
            throw (function $L(e, t) {
              return new v(3400, !1);
            })();
          const o = _t(this._elementListeners, t, []),
            s = { name: n, phase: r, callback: i };
          o.push(s);
          const a = _t(this._engine.statesByElement, t, new Map());
          return (
            a.has(n) || (Ot(t, Pc), Ot(t, Pc + "-" + n), a.set(n, Fh)),
            () => {
              this._engine.afterFlush(() => {
                const c = o.indexOf(s);
                c >= 0 && o.splice(c, 1), this._triggers.has(n) || a.delete(n);
              });
            }
          );
        }
        register(t, n) {
          return !this._triggers.has(t) && (this._triggers.set(t, n), !0);
        }
        _getTrigger(t) {
          const n = this._triggers.get(t);
          if (!n)
            throw (function UL(e) {
              return new v(3401, !1);
            })();
          return n;
        }
        trigger(t, n, r, i = !0) {
          const o = this._getTrigger(n),
            s = new Lh(this.id, n, t);
          let a = this._engine.statesByElement.get(t);
          a ||
            (Ot(t, Pc),
            Ot(t, Pc + "-" + n),
            this._engine.statesByElement.set(t, (a = new Map())));
          let c = a.get(n);
          const l = new kh(r, this.id);
          if (
            (!(r && r.hasOwnProperty("value")) &&
              c &&
              l.absorbOptions(c.options),
            a.set(n, l),
            c || (c = Fh),
            l.value !== ps && c.value === l.value)
          ) {
            if (
              !(function q2(e, t) {
                const n = Object.keys(e),
                  r = Object.keys(t);
                if (n.length != r.length) return !1;
                for (let i = 0; i < n.length; i++) {
                  const o = n[i];
                  if (!t.hasOwnProperty(o) || e[o] !== t[o]) return !1;
                }
                return !0;
              })(c.params, l.params)
            ) {
              const m = [],
                g = o.matchStyles(c.value, c.params, m),
                y = o.matchStyles(l.value, l.params, m);
              m.length
                ? this._engine.reportError(m)
                : this._engine.afterFlush(() => {
                    Cr(t, g), ln(t, y);
                  });
            }
            return;
          }
          const f = _t(this._engine.playersByElement, t, []);
          f.forEach((m) => {
            m.namespaceId == this.id &&
              m.triggerName == n &&
              m.queued &&
              m.destroy();
          });
          let h = o.matchTransition(c.value, l.value, t, l.params),
            p = !1;
          if (!h) {
            if (!i) return;
            (h = o.fallbackTransition), (p = !0);
          }
          return (
            this._engine.totalQueuedPlayers++,
            this._queue.push({
              element: t,
              triggerName: n,
              transition: h,
              fromState: c,
              toState: l,
              player: s,
              isFallbackTransition: p,
            }),
            p ||
              (Ot(t, rw),
              s.onStart(() => {
                Fi(t, rw);
              })),
            s.onDone(() => {
              let m = this.players.indexOf(s);
              m >= 0 && this.players.splice(m, 1);
              const g = this._engine.playersByElement.get(t);
              if (g) {
                let y = g.indexOf(s);
                y >= 0 && g.splice(y, 1);
              }
            }),
            this.players.push(s),
            f.push(s),
            s
          );
        }
        deregister(t) {
          this._triggers.delete(t),
            this._engine.statesByElement.forEach((n) => n.delete(t)),
            this._elementListeners.forEach((n, r) => {
              this._elementListeners.set(
                r,
                n.filter((i) => i.name != t),
              );
            });
        }
        clearElementCache(t) {
          this._engine.statesByElement.delete(t),
            this._elementListeners.delete(t);
          const n = this._engine.playersByElement.get(t);
          n &&
            (n.forEach((r) => r.destroy()),
            this._engine.playersByElement.delete(t));
        }
        _signalRemovalForInnerTriggers(t, n) {
          const r = this._engine.driver.query(t, kc, !0);
          r.forEach((i) => {
            if (i[qt]) return;
            const o = this._engine.fetchNamespacesByElement(i);
            o.size
              ? o.forEach((s) => s.triggerLeaveAnimation(i, n, !1, !0))
              : this.clearElementCache(i);
          }),
            this._engine.afterFlushAnimationsDone(() =>
              r.forEach((i) => this.clearElementCache(i)),
            );
        }
        triggerLeaveAnimation(t, n, r, i) {
          const o = this._engine.statesByElement.get(t),
            s = new Map();
          if (o) {
            const a = [];
            if (
              (o.forEach((c, l) => {
                if ((s.set(l, c.value), this._triggers.has(l))) {
                  const u = this.trigger(t, l, ps, i);
                  u && a.push(u);
                }
              }),
              a.length)
            )
              return (
                this._engine.markElementAsRemoved(this.id, t, !0, n, s),
                r && Zn(a).onDone(() => this._engine.processLeaveNode(t)),
                !0
              );
          }
          return !1;
        }
        prepareLeaveAnimationListeners(t) {
          const n = this._elementListeners.get(t),
            r = this._engine.statesByElement.get(t);
          if (n && r) {
            const i = new Set();
            n.forEach((o) => {
              const s = o.name;
              if (i.has(s)) return;
              i.add(s);
              const c = this._triggers.get(s).fallbackTransition,
                l = r.get(s) || Fh,
                u = new kh(ps),
                d = new Lh(this.id, s, t);
              this._engine.totalQueuedPlayers++,
                this._queue.push({
                  element: t,
                  triggerName: s,
                  transition: c,
                  fromState: l,
                  toState: u,
                  player: d,
                  isFallbackTransition: !0,
                });
            });
          }
        }
        removeNode(t, n) {
          const r = this._engine;
          if (
            (t.childElementCount && this._signalRemovalForInnerTriggers(t, n),
            this.triggerLeaveAnimation(t, n, !0))
          )
            return;
          let i = !1;
          if (r.totalAnimations) {
            const o = r.players.length ? r.playersByQueriedElement.get(t) : [];
            if (o && o.length) i = !0;
            else {
              let s = t;
              for (; (s = s.parentNode); )
                if (r.statesByElement.get(s)) {
                  i = !0;
                  break;
                }
            }
          }
          if ((this.prepareLeaveAnimationListeners(t), i))
            r.markElementAsRemoved(this.id, t, !1, n);
          else {
            const o = t[qt];
            (!o || o === iw) &&
              (r.afterFlush(() => this.clearElementCache(t)),
              r.destroyInnerAnimations(t),
              r._onRemovalComplete(t, n));
          }
        }
        insertNode(t, n) {
          Ot(t, this._hostClassName);
        }
        drainQueuedTransitions(t) {
          const n = [];
          return (
            this._queue.forEach((r) => {
              const i = r.player;
              if (i.destroyed) return;
              const o = r.element,
                s = this._elementListeners.get(o);
              s &&
                s.forEach((a) => {
                  if (a.name == r.triggerName) {
                    const c = vh(
                      o,
                      r.triggerName,
                      r.fromState.value,
                      r.toState.value,
                    );
                    (c._data = t), bh(r.player, a.phase, c, a.callback);
                  }
                }),
                i.markedForDestroy
                  ? this._engine.afterFlush(() => {
                      i.destroy();
                    })
                  : n.push(r);
            }),
            (this._queue = []),
            n.sort((r, i) => {
              const o = r.transition.ast.depCount,
                s = i.transition.ast.depCount;
              return 0 == o || 0 == s
                ? o - s
                : this._engine.driver.containsElement(r.element, i.element)
                ? 1
                : -1;
            })
          );
        }
        destroy(t) {
          this.players.forEach((n) => n.destroy()),
            this._signalRemovalForInnerTriggers(this.hostElement, t);
        }
      }
      class B2 {
        _onRemovalComplete(t, n) {
          this.onRemovalComplete(t, n);
        }
        constructor(t, n, r) {
          (this.bodyNode = t),
            (this.driver = n),
            (this._normalizer = r),
            (this.players = []),
            (this.newHostElements = new Map()),
            (this.playersByElement = new Map()),
            (this.playersByQueriedElement = new Map()),
            (this.statesByElement = new Map()),
            (this.disabledNodes = new Set()),
            (this.totalAnimations = 0),
            (this.totalQueuedPlayers = 0),
            (this._namespaceLookup = {}),
            (this._namespaceList = []),
            (this._flushFns = []),
            (this._whenQuietFns = []),
            (this.namespacesByHostElement = new Map()),
            (this.collectedEnterElements = []),
            (this.collectedLeaveElements = []),
            (this.onRemovalComplete = (i, o) => {});
        }
        get queuedPlayers() {
          const t = [];
          return (
            this._namespaceList.forEach((n) => {
              n.players.forEach((r) => {
                r.queued && t.push(r);
              });
            }),
            t
          );
        }
        createNamespace(t, n) {
          const r = new j2(t, n, this);
          return (
            this.bodyNode && this.driver.containsElement(this.bodyNode, n)
              ? this._balanceNamespaceList(r, n)
              : (this.newHostElements.set(n, r), this.collectEnterElement(n)),
            (this._namespaceLookup[t] = r)
          );
        }
        _balanceNamespaceList(t, n) {
          const r = this._namespaceList,
            i = this.namespacesByHostElement;
          if (r.length - 1 >= 0) {
            let s = !1,
              a = this.driver.getParentElement(n);
            for (; a; ) {
              const c = i.get(a);
              if (c) {
                const l = r.indexOf(c);
                r.splice(l + 1, 0, t), (s = !0);
                break;
              }
              a = this.driver.getParentElement(a);
            }
            s || r.unshift(t);
          } else r.push(t);
          return i.set(n, t), t;
        }
        register(t, n) {
          let r = this._namespaceLookup[t];
          return r || (r = this.createNamespace(t, n)), r;
        }
        registerTrigger(t, n, r) {
          let i = this._namespaceLookup[t];
          i && i.register(n, r) && this.totalAnimations++;
        }
        destroy(t, n) {
          t &&
            (this.afterFlush(() => {}),
            this.afterFlushAnimationsDone(() => {
              const r = this._fetchNamespace(t);
              this.namespacesByHostElement.delete(r.hostElement);
              const i = this._namespaceList.indexOf(r);
              i >= 0 && this._namespaceList.splice(i, 1),
                r.destroy(n),
                delete this._namespaceLookup[t];
            }));
        }
        _fetchNamespace(t) {
          return this._namespaceLookup[t];
        }
        fetchNamespacesByElement(t) {
          const n = new Set(),
            r = this.statesByElement.get(t);
          if (r)
            for (let i of r.values())
              if (i.namespaceId) {
                const o = this._fetchNamespace(i.namespaceId);
                o && n.add(o);
              }
          return n;
        }
        trigger(t, n, r, i) {
          if (zc(n)) {
            const o = this._fetchNamespace(t);
            if (o) return o.trigger(n, r, i), !0;
          }
          return !1;
        }
        insertNode(t, n, r, i) {
          if (!zc(n)) return;
          const o = n[qt];
          if (o && o.setForRemoval) {
            (o.setForRemoval = !1), (o.setForMove = !0);
            const s = this.collectedLeaveElements.indexOf(n);
            s >= 0 && this.collectedLeaveElements.splice(s, 1);
          }
          if (t) {
            const s = this._fetchNamespace(t);
            s && s.insertNode(n, r);
          }
          i && this.collectEnterElement(n);
        }
        collectEnterElement(t) {
          this.collectedEnterElements.push(t);
        }
        markElementAsDisabled(t, n) {
          n
            ? this.disabledNodes.has(t) ||
              (this.disabledNodes.add(t), Ot(t, Ph))
            : this.disabledNodes.has(t) &&
              (this.disabledNodes.delete(t), Fi(t, Ph));
        }
        removeNode(t, n, r) {
          if (zc(n)) {
            const i = t ? this._fetchNamespace(t) : null;
            i ? i.removeNode(n, r) : this.markElementAsRemoved(t, n, !1, r);
            const o = this.namespacesByHostElement.get(n);
            o && o.id !== t && o.removeNode(n, r);
          } else this._onRemovalComplete(n, r);
        }
        markElementAsRemoved(t, n, r, i, o) {
          this.collectedLeaveElements.push(n),
            (n[qt] = {
              namespaceId: t,
              setForRemoval: i,
              hasAnimation: r,
              removedBeforeQueried: !1,
              previousTriggersValues: o,
            });
        }
        listen(t, n, r, i, o) {
          return zc(n) ? this._fetchNamespace(t).listen(n, r, i, o) : () => {};
        }
        _buildInstruction(t, n, r, i, o) {
          return t.transition.build(
            this.driver,
            t.element,
            t.fromState.value,
            t.toState.value,
            r,
            i,
            t.fromState.options,
            t.toState.options,
            n,
            o,
          );
        }
        destroyInnerAnimations(t) {
          let n = this.driver.query(t, kc, !0);
          n.forEach((r) => this.destroyActiveAnimationsForElement(r)),
            0 != this.playersByQueriedElement.size &&
              ((n = this.driver.query(t, Eh, !0)),
              n.forEach((r) => this.finishActiveQueriedAnimationOnElement(r)));
        }
        destroyActiveAnimationsForElement(t) {
          const n = this.playersByElement.get(t);
          n &&
            n.forEach((r) => {
              r.queued ? (r.markedForDestroy = !0) : r.destroy();
            });
        }
        finishActiveQueriedAnimationOnElement(t) {
          const n = this.playersByQueriedElement.get(t);
          n && n.forEach((r) => r.finish());
        }
        whenRenderingDone() {
          return new Promise((t) => {
            if (this.players.length) return Zn(this.players).onDone(() => t());
            t();
          });
        }
        processLeaveNode(t) {
          const n = t[qt];
          if (n && n.setForRemoval) {
            if (((t[qt] = iw), n.namespaceId)) {
              this.destroyInnerAnimations(t);
              const r = this._fetchNamespace(n.namespaceId);
              r && r.clearElementCache(t);
            }
            this._onRemovalComplete(t, n.setForRemoval);
          }
          t.classList?.contains(Ph) && this.markElementAsDisabled(t, !1),
            this.driver.query(t, ".ng-animate-disabled", !0).forEach((r) => {
              this.markElementAsDisabled(r, !1);
            });
        }
        flush(t = -1) {
          let n = [];
          if (
            (this.newHostElements.size &&
              (this.newHostElements.forEach((r, i) =>
                this._balanceNamespaceList(r, i),
              ),
              this.newHostElements.clear()),
            this.totalAnimations && this.collectedEnterElements.length)
          )
            for (let r = 0; r < this.collectedEnterElements.length; r++)
              Ot(this.collectedEnterElements[r], "ng-star-inserted");
          if (
            this._namespaceList.length &&
            (this.totalQueuedPlayers || this.collectedLeaveElements.length)
          ) {
            const r = [];
            try {
              n = this._flushAnimations(r, t);
            } finally {
              for (let i = 0; i < r.length; i++) r[i]();
            }
          } else
            for (let r = 0; r < this.collectedLeaveElements.length; r++)
              this.processLeaveNode(this.collectedLeaveElements[r]);
          if (
            ((this.totalQueuedPlayers = 0),
            (this.collectedEnterElements.length = 0),
            (this.collectedLeaveElements.length = 0),
            this._flushFns.forEach((r) => r()),
            (this._flushFns = []),
            this._whenQuietFns.length)
          ) {
            const r = this._whenQuietFns;
            (this._whenQuietFns = []),
              n.length
                ? Zn(n).onDone(() => {
                    r.forEach((i) => i());
                  })
                : r.forEach((i) => i());
          }
        }
        reportError(t) {
          throw (function HL(e) {
            return new v(3402, !1);
          })();
        }
        _flushAnimations(t, n) {
          const r = new $c(),
            i = [],
            o = new Map(),
            s = [],
            a = new Map(),
            c = new Map(),
            l = new Map(),
            u = new Set();
          this.disabledNodes.forEach((T) => {
            u.add(T);
            const N = this.driver.query(T, ".ng-animate-queued", !0);
            for (let R = 0; R < N.length; R++) u.add(N[R]);
          });
          const d = this.bodyNode,
            f = Array.from(this.statesByElement.keys()),
            h = aw(f, this.collectedEnterElements),
            p = new Map();
          let m = 0;
          h.forEach((T, N) => {
            const R = wh + m++;
            p.set(N, R), T.forEach((K) => Ot(K, R));
          });
          const g = [],
            y = new Set(),
            b = new Set();
          for (let T = 0; T < this.collectedLeaveElements.length; T++) {
            const N = this.collectedLeaveElements[T],
              R = N[qt];
            R &&
              R.setForRemoval &&
              (g.push(N),
              y.add(N),
              R.hasAnimation
                ? this.driver
                    .query(N, ".ng-star-inserted", !0)
                    .forEach((K) => y.add(K))
                : b.add(N));
          }
          const w = new Map(),
            M = aw(f, Array.from(y));
          M.forEach((T, N) => {
            const R = Oc + m++;
            w.set(N, R), T.forEach((K) => Ot(K, R));
          }),
            t.push(() => {
              h.forEach((T, N) => {
                const R = p.get(N);
                T.forEach((K) => Fi(K, R));
              }),
                M.forEach((T, N) => {
                  const R = w.get(N);
                  T.forEach((K) => Fi(K, R));
                }),
                g.forEach((T) => {
                  this.processLeaveNode(T);
                });
            });
          const F = [],
            te = [];
          for (let T = this._namespaceList.length - 1; T >= 0; T--)
            this._namespaceList[T].drainQueuedTransitions(n).forEach((R) => {
              const K = R.player,
                xe = R.element;
              if ((F.push(K), this.collectedEnterElements.length)) {
                const qe = xe[qt];
                if (qe && qe.setForMove) {
                  if (
                    qe.previousTriggersValues &&
                    qe.previousTriggersValues.has(R.triggerName)
                  ) {
                    const kr = qe.previousTriggersValues.get(R.triggerName),
                      kt = this.statesByElement.get(R.element);
                    if (kt && kt.has(R.triggerName)) {
                      const xl = kt.get(R.triggerName);
                      (xl.value = kr), kt.set(R.triggerName, xl);
                    }
                  }
                  return void K.destroy();
                }
              }
              const hn = !d || !this.driver.containsElement(d, xe),
                Et = w.get(xe),
                nr = p.get(xe),
                he = this._buildInstruction(R, r, nr, Et, hn);
              if (he.errors && he.errors.length) return void te.push(he);
              if (hn)
                return (
                  K.onStart(() => Cr(xe, he.fromStyles)),
                  K.onDestroy(() => ln(xe, he.toStyles)),
                  void i.push(K)
                );
              if (R.isFallbackTransition)
                return (
                  K.onStart(() => Cr(xe, he.fromStyles)),
                  K.onDestroy(() => ln(xe, he.toStyles)),
                  void i.push(K)
                );
              const xC = [];
              he.timelines.forEach((qe) => {
                (qe.stretchStartingKeyframe = !0),
                  this.disabledNodes.has(qe.element) || xC.push(qe);
              }),
                (he.timelines = xC),
                r.append(xe, he.timelines),
                s.push({ instruction: he, player: K, element: xe }),
                he.queriedElements.forEach((qe) => _t(a, qe, []).push(K)),
                he.preStyleProps.forEach((qe, kr) => {
                  if (qe.size) {
                    let kt = c.get(kr);
                    kt || c.set(kr, (kt = new Set())),
                      qe.forEach((xl, _p) => kt.add(_p));
                  }
                }),
                he.postStyleProps.forEach((qe, kr) => {
                  let kt = l.get(kr);
                  kt || l.set(kr, (kt = new Set())),
                    qe.forEach((xl, _p) => kt.add(_p));
                });
            });
          if (te.length) {
            const T = [];
            te.forEach((N) => {
              T.push(
                (function zL(e, t) {
                  return new v(3505, !1);
                })(),
              );
            }),
              F.forEach((N) => N.destroy()),
              this.reportError(T);
          }
          const ue = new Map(),
            Le = new Map();
          s.forEach((T) => {
            const N = T.element;
            r.has(N) &&
              (Le.set(N, N),
              this._beforeAnimationBuild(
                T.player.namespaceId,
                T.instruction,
                ue,
              ));
          }),
            i.forEach((T) => {
              const N = T.element;
              this._getPreviousPlayers(
                N,
                !1,
                T.namespaceId,
                T.triggerName,
                null,
              ).forEach((K) => {
                _t(ue, N, []).push(K), K.destroy();
              });
            });
          const wt = g.filter((T) => lw(T, c, l)),
            Kt = new Map();
          sw(Kt, this.driver, b, l, Tn).forEach((T) => {
            lw(T, c, l) && wt.push(T);
          });
          const js = new Map();
          h.forEach((T, N) => {
            sw(js, this.driver, new Set(T), c, "!");
          }),
            wt.forEach((T) => {
              const N = Kt.get(T),
                R = js.get(T);
              Kt.set(
                T,
                new Map([...(N?.entries() ?? []), ...(R?.entries() ?? [])]),
              );
            });
          const Pr = [],
            MC = [],
            SC = {};
          s.forEach((T) => {
            const { element: N, player: R, instruction: K } = T;
            if (r.has(N)) {
              if (u.has(N))
                return (
                  R.onDestroy(() => ln(N, K.toStyles)),
                  (R.disabled = !0),
                  R.overrideTotalTime(K.totalTime),
                  void i.push(R)
                );
              let xe = SC;
              if (Le.size > 1) {
                let Et = N;
                const nr = [];
                for (; (Et = Et.parentNode); ) {
                  const he = Le.get(Et);
                  if (he) {
                    xe = he;
                    break;
                  }
                  nr.push(Et);
                }
                nr.forEach((he) => Le.set(he, xe));
              }
              const hn = this._buildAnimation(R.namespaceId, K, ue, o, js, Kt);
              if ((R.setRealPlayer(hn), xe === SC)) Pr.push(R);
              else {
                const Et = this.playersByElement.get(xe);
                Et && Et.length && (R.parentPlayer = Zn(Et)), i.push(R);
              }
            } else
              Cr(N, K.fromStyles),
                R.onDestroy(() => ln(N, K.toStyles)),
                MC.push(R),
                u.has(N) && i.push(R);
          }),
            MC.forEach((T) => {
              const N = o.get(T.element);
              if (N && N.length) {
                const R = Zn(N);
                T.setRealPlayer(R);
              }
            }),
            i.forEach((T) => {
              T.parentPlayer ? T.syncPlayerEvents(T.parentPlayer) : T.destroy();
            });
          for (let T = 0; T < g.length; T++) {
            const N = g[T],
              R = N[qt];
            if ((Fi(N, Oc), R && R.hasAnimation)) continue;
            let K = [];
            if (a.size) {
              let hn = a.get(N);
              hn && hn.length && K.push(...hn);
              let Et = this.driver.query(N, Eh, !0);
              for (let nr = 0; nr < Et.length; nr++) {
                let he = a.get(Et[nr]);
                he && he.length && K.push(...he);
              }
            }
            const xe = K.filter((hn) => !hn.destroyed);
            xe.length ? H2(this, N, xe) : this.processLeaveNode(N);
          }
          return (
            (g.length = 0),
            Pr.forEach((T) => {
              this.players.push(T),
                T.onDone(() => {
                  T.destroy();
                  const N = this.players.indexOf(T);
                  this.players.splice(N, 1);
                }),
                T.play();
            }),
            Pr
          );
        }
        afterFlush(t) {
          this._flushFns.push(t);
        }
        afterFlushAnimationsDone(t) {
          this._whenQuietFns.push(t);
        }
        _getPreviousPlayers(t, n, r, i, o) {
          let s = [];
          if (n) {
            const a = this.playersByQueriedElement.get(t);
            a && (s = a);
          } else {
            const a = this.playersByElement.get(t);
            if (a) {
              const c = !o || o == ps;
              a.forEach((l) => {
                l.queued || (!c && l.triggerName != i) || s.push(l);
              });
            }
          }
          return (
            (r || i) &&
              (s = s.filter(
                (a) =>
                  !((r && r != a.namespaceId) || (i && i != a.triggerName)),
              )),
            s
          );
        }
        _beforeAnimationBuild(t, n, r) {
          const o = n.element,
            s = n.isRemovalTransition ? void 0 : t,
            a = n.isRemovalTransition ? void 0 : n.triggerName;
          for (const c of n.timelines) {
            const l = c.element,
              u = l !== o,
              d = _t(r, l, []);
            this._getPreviousPlayers(l, u, s, a, n.toState).forEach((h) => {
              const p = h.getRealPlayer();
              p.beforeDestroy && p.beforeDestroy(), h.destroy(), d.push(h);
            });
          }
          Cr(o, n.fromStyles);
        }
        _buildAnimation(t, n, r, i, o, s) {
          const a = n.triggerName,
            c = n.element,
            l = [],
            u = new Set(),
            d = new Set(),
            f = n.timelines.map((p) => {
              const m = p.element;
              u.add(m);
              const g = m[qt];
              if (g && g.removedBeforeQueried)
                return new us(p.duration, p.delay);
              const y = m !== c,
                b = (function z2(e) {
                  const t = [];
                  return cw(e, t), t;
                })((r.get(m) || F2).map((ue) => ue.getRealPlayer())).filter(
                  (ue) => !!ue.element && ue.element === m,
                ),
                w = o.get(m),
                M = s.get(m),
                F = jD(this._normalizer, p.keyframes, w, M),
                te = this._buildPlayer(p, F, b);
              if ((p.subTimeline && i && d.add(m), y)) {
                const ue = new Lh(t, a, m);
                ue.setRealPlayer(te), l.push(ue);
              }
              return te;
            });
          l.forEach((p) => {
            _t(this.playersByQueriedElement, p.element, []).push(p),
              p.onDone(() =>
                (function V2(e, t, n) {
                  let r = e.get(t);
                  if (r) {
                    if (r.length) {
                      const i = r.indexOf(n);
                      r.splice(i, 1);
                    }
                    0 == r.length && e.delete(t);
                  }
                  return r;
                })(this.playersByQueriedElement, p.element, p),
              );
          }),
            u.forEach((p) => Ot(p, qD));
          const h = Zn(f);
          return (
            h.onDestroy(() => {
              u.forEach((p) => Fi(p, qD)), ln(c, n.toStyles);
            }),
            d.forEach((p) => {
              _t(i, p, []).push(h);
            }),
            h
          );
        }
        _buildPlayer(t, n, r) {
          return n.length > 0
            ? this.driver.animate(
                t.element,
                n,
                t.duration,
                t.delay,
                t.easing,
                r,
              )
            : new us(t.duration, t.delay);
        }
      }
      class Lh {
        constructor(t, n, r) {
          (this.namespaceId = t),
            (this.triggerName = n),
            (this.element = r),
            (this._player = new us()),
            (this._containsRealPlayer = !1),
            (this._queuedCallbacks = new Map()),
            (this.destroyed = !1),
            (this.parentPlayer = null),
            (this.markedForDestroy = !1),
            (this.disabled = !1),
            (this.queued = !0),
            (this.totalTime = 0);
        }
        setRealPlayer(t) {
          this._containsRealPlayer ||
            ((this._player = t),
            this._queuedCallbacks.forEach((n, r) => {
              n.forEach((i) => bh(t, r, void 0, i));
            }),
            this._queuedCallbacks.clear(),
            (this._containsRealPlayer = !0),
            this.overrideTotalTime(t.totalTime),
            (this.queued = !1));
        }
        getRealPlayer() {
          return this._player;
        }
        overrideTotalTime(t) {
          this.totalTime = t;
        }
        syncPlayerEvents(t) {
          const n = this._player;
          n.triggerCallback && t.onStart(() => n.triggerCallback("start")),
            t.onDone(() => this.finish()),
            t.onDestroy(() => this.destroy());
        }
        _queueEvent(t, n) {
          _t(this._queuedCallbacks, t, []).push(n);
        }
        onDone(t) {
          this.queued && this._queueEvent("done", t), this._player.onDone(t);
        }
        onStart(t) {
          this.queued && this._queueEvent("start", t), this._player.onStart(t);
        }
        onDestroy(t) {
          this.queued && this._queueEvent("destroy", t),
            this._player.onDestroy(t);
        }
        init() {
          this._player.init();
        }
        hasStarted() {
          return !this.queued && this._player.hasStarted();
        }
        play() {
          !this.queued && this._player.play();
        }
        pause() {
          !this.queued && this._player.pause();
        }
        restart() {
          !this.queued && this._player.restart();
        }
        finish() {
          this._player.finish();
        }
        destroy() {
          (this.destroyed = !0), this._player.destroy();
        }
        reset() {
          !this.queued && this._player.reset();
        }
        setPosition(t) {
          this.queued || this._player.setPosition(t);
        }
        getPosition() {
          return this.queued ? 0 : this._player.getPosition();
        }
        triggerCallback(t) {
          const n = this._player;
          n.triggerCallback && n.triggerCallback(t);
        }
      }
      function zc(e) {
        return e && 1 === e.nodeType;
      }
      function ow(e, t) {
        const n = e.style.display;
        return (e.style.display = t ?? "none"), n;
      }
      function sw(e, t, n, r, i) {
        const o = [];
        n.forEach((c) => o.push(ow(c)));
        const s = [];
        r.forEach((c, l) => {
          const u = new Map();
          c.forEach((d) => {
            const f = t.computeStyle(l, d, i);
            u.set(d, f), (!f || 0 == f.length) && ((l[qt] = L2), s.push(l));
          }),
            e.set(l, u);
        });
        let a = 0;
        return n.forEach((c) => ow(c, o[a++])), s;
      }
      function aw(e, t) {
        const n = new Map();
        if ((e.forEach((a) => n.set(a, [])), 0 == t.length)) return n;
        const i = new Set(t),
          o = new Map();
        function s(a) {
          if (!a) return 1;
          let c = o.get(a);
          if (c) return c;
          const l = a.parentNode;
          return (c = n.has(l) ? l : i.has(l) ? 1 : s(l)), o.set(a, c), c;
        }
        return (
          t.forEach((a) => {
            const c = s(a);
            1 !== c && n.get(c).push(a);
          }),
          n
        );
      }
      function Ot(e, t) {
        e.classList?.add(t);
      }
      function Fi(e, t) {
        e.classList?.remove(t);
      }
      function H2(e, t, n) {
        Zn(n).onDone(() => e.processLeaveNode(t));
      }
      function cw(e, t) {
        for (let n = 0; n < e.length; n++) {
          const r = e[n];
          r instanceof FD ? cw(r.players, t) : t.push(r);
        }
      }
      function lw(e, t, n) {
        const r = n.get(e);
        if (!r) return !1;
        let i = t.get(e);
        return i ? r.forEach((o) => i.add(o)) : t.set(e, r), n.delete(e), !0;
      }
      class qc {
        constructor(t, n, r) {
          (this.bodyNode = t),
            (this._driver = n),
            (this._normalizer = r),
            (this._triggerCache = {}),
            (this.onRemovalComplete = (i, o) => {}),
            (this._transitionEngine = new B2(t, n, r)),
            (this._timelineEngine = new N2(t, n, r)),
            (this._transitionEngine.onRemovalComplete = (i, o) =>
              this.onRemovalComplete(i, o));
        }
        registerTrigger(t, n, r, i, o) {
          const s = t + "-" + i;
          let a = this._triggerCache[s];
          if (!a) {
            const c = [],
              u = Sh(this._driver, o, c, []);
            if (c.length)
              throw (function OL(e, t) {
                return new v(3404, !1);
              })();
            (a = (function S2(e, t, n) {
              return new x2(e, t, n);
            })(i, u, this._normalizer)),
              (this._triggerCache[s] = a);
          }
          this._transitionEngine.registerTrigger(n, i, a);
        }
        register(t, n) {
          this._transitionEngine.register(t, n);
        }
        destroy(t, n) {
          this._transitionEngine.destroy(t, n);
        }
        onInsert(t, n, r, i) {
          this._transitionEngine.insertNode(t, n, r, i);
        }
        onRemove(t, n, r) {
          this._transitionEngine.removeNode(t, n, r);
        }
        disableAnimations(t, n) {
          this._transitionEngine.markElementAsDisabled(t, n);
        }
        process(t, n, r, i) {
          if ("@" == r.charAt(0)) {
            const [o, s] = BD(r);
            this._timelineEngine.command(o, n, s, i);
          } else this._transitionEngine.trigger(t, n, r, i);
        }
        listen(t, n, r, i, o) {
          if ("@" == r.charAt(0)) {
            const [s, a] = BD(r);
            return this._timelineEngine.listen(s, n, a, o);
          }
          return this._transitionEngine.listen(t, n, r, i, o);
        }
        flush(t = -1) {
          this._transitionEngine.flush(t);
        }
        get players() {
          return [
            ...this._transitionEngine.players,
            ...this._timelineEngine.players,
          ];
        }
        whenRenderingDone() {
          return this._transitionEngine.whenRenderingDone();
        }
        afterFlushAnimationsDone(t) {
          this._transitionEngine.afterFlushAnimationsDone(t);
        }
      }
      let W2 = (() => {
        class e {
          static {
            this.initialStylesByElement = new WeakMap();
          }
          constructor(n, r, i) {
            (this._element = n),
              (this._startStyles = r),
              (this._endStyles = i),
              (this._state = 0);
            let o = e.initialStylesByElement.get(n);
            o || e.initialStylesByElement.set(n, (o = new Map())),
              (this._initialStyles = o);
          }
          start() {
            this._state < 1 &&
              (this._startStyles &&
                ln(this._element, this._startStyles, this._initialStyles),
              (this._state = 1));
          }
          finish() {
            this.start(),
              this._state < 2 &&
                (ln(this._element, this._initialStyles),
                this._endStyles &&
                  (ln(this._element, this._endStyles),
                  (this._endStyles = null)),
                (this._state = 1));
          }
          destroy() {
            this.finish(),
              this._state < 3 &&
                (e.initialStylesByElement.delete(this._element),
                this._startStyles &&
                  (Cr(this._element, this._startStyles),
                  (this._endStyles = null)),
                this._endStyles &&
                  (Cr(this._element, this._endStyles),
                  (this._endStyles = null)),
                ln(this._element, this._initialStyles),
                (this._state = 3));
          }
        }
        return e;
      })();
      function jh(e) {
        let t = null;
        return (
          e.forEach((n, r) => {
            (function K2(e) {
              return "display" === e || "position" === e;
            })(r) && ((t = t || new Map()), t.set(r, n));
          }),
          t
        );
      }
      class uw {
        constructor(t, n, r, i) {
          (this.element = t),
            (this.keyframes = n),
            (this.options = r),
            (this._specialStyles = i),
            (this._onDoneFns = []),
            (this._onStartFns = []),
            (this._onDestroyFns = []),
            (this._initialized = !1),
            (this._finished = !1),
            (this._started = !1),
            (this._destroyed = !1),
            (this._originalOnDoneFns = []),
            (this._originalOnStartFns = []),
            (this.time = 0),
            (this.parentPlayer = null),
            (this.currentSnapshot = new Map()),
            (this._duration = r.duration),
            (this._delay = r.delay || 0),
            (this.time = this._duration + this._delay);
        }
        _onFinish() {
          this._finished ||
            ((this._finished = !0),
            this._onDoneFns.forEach((t) => t()),
            (this._onDoneFns = []));
        }
        init() {
          this._buildPlayer(), this._preparePlayerBeforeStart();
        }
        _buildPlayer() {
          if (this._initialized) return;
          this._initialized = !0;
          const t = this.keyframes;
          (this.domPlayer = this._triggerWebAnimation(
            this.element,
            t,
            this.options,
          )),
            (this._finalKeyframe = t.length ? t[t.length - 1] : new Map());
          const n = () => this._onFinish();
          this.domPlayer.addEventListener("finish", n),
            this.onDestroy(() => {
              this.domPlayer.removeEventListener("finish", n);
            });
        }
        _preparePlayerBeforeStart() {
          this._delay ? this._resetDomPlayerState() : this.domPlayer.pause();
        }
        _convertKeyframesToObject(t) {
          const n = [];
          return (
            t.forEach((r) => {
              n.push(Object.fromEntries(r));
            }),
            n
          );
        }
        _triggerWebAnimation(t, n, r) {
          return t.animate(this._convertKeyframesToObject(n), r);
        }
        onStart(t) {
          this._originalOnStartFns.push(t), this._onStartFns.push(t);
        }
        onDone(t) {
          this._originalOnDoneFns.push(t), this._onDoneFns.push(t);
        }
        onDestroy(t) {
          this._onDestroyFns.push(t);
        }
        play() {
          this._buildPlayer(),
            this.hasStarted() ||
              (this._onStartFns.forEach((t) => t()),
              (this._onStartFns = []),
              (this._started = !0),
              this._specialStyles && this._specialStyles.start()),
            this.domPlayer.play();
        }
        pause() {
          this.init(), this.domPlayer.pause();
        }
        finish() {
          this.init(),
            this._specialStyles && this._specialStyles.finish(),
            this._onFinish(),
            this.domPlayer.finish();
        }
        reset() {
          this._resetDomPlayerState(),
            (this._destroyed = !1),
            (this._finished = !1),
            (this._started = !1),
            (this._onStartFns = this._originalOnStartFns),
            (this._onDoneFns = this._originalOnDoneFns);
        }
        _resetDomPlayerState() {
          this.domPlayer && this.domPlayer.cancel();
        }
        restart() {
          this.reset(), this.play();
        }
        hasStarted() {
          return this._started;
        }
        destroy() {
          this._destroyed ||
            ((this._destroyed = !0),
            this._resetDomPlayerState(),
            this._onFinish(),
            this._specialStyles && this._specialStyles.destroy(),
            this._onDestroyFns.forEach((t) => t()),
            (this._onDestroyFns = []));
        }
        setPosition(t) {
          void 0 === this.domPlayer && this.init(),
            (this.domPlayer.currentTime = t * this.time);
        }
        getPosition() {
          return +(this.domPlayer.currentTime ?? 0) / this.time;
        }
        get totalTime() {
          return this._delay + this._duration;
        }
        beforeDestroy() {
          const t = new Map();
          this.hasStarted() &&
            this._finalKeyframe.forEach((r, i) => {
              "offset" !== i &&
                t.set(i, this._finished ? r : ZD(this.element, i));
            }),
            (this.currentSnapshot = t);
        }
        triggerCallback(t) {
          const n = "start" === t ? this._onStartFns : this._onDoneFns;
          n.forEach((r) => r()), (n.length = 0);
        }
      }
      class Z2 {
        validateStyleProperty(t) {
          return !0;
        }
        validateAnimatableStyleProperty(t) {
          return !0;
        }
        matchesElement(t, n) {
          return !1;
        }
        containsElement(t, n) {
          return $D(t, n);
        }
        getParentElement(t) {
          return _h(t);
        }
        query(t, n, r) {
          return UD(t, n, r);
        }
        computeStyle(t, n, r) {
          return window.getComputedStyle(t)[n];
        }
        animate(t, n, r, i, o, s = []) {
          const c = {
            duration: r,
            delay: i,
            fill: 0 == i ? "both" : "forwards",
          };
          o && (c.easing = o);
          const l = new Map(),
            u = s.filter((h) => h instanceof uw);
          (function n2(e, t) {
            return 0 === e || 0 === t;
          })(r, i) &&
            u.forEach((h) => {
              h.currentSnapshot.forEach((p, m) => l.set(m, p));
            });
          let d = (function JL(e) {
            return e.length
              ? e[0] instanceof Map
                ? e
                : e.map((t) => GD(t))
              : [];
          })(n).map((h) => Qn(h));
          d = (function r2(e, t, n) {
            if (n.size && t.length) {
              let r = t[0],
                i = [];
              if (
                (n.forEach((o, s) => {
                  r.has(s) || i.push(s), r.set(s, o);
                }),
                i.length)
              )
                for (let o = 1; o < t.length; o++) {
                  let s = t[o];
                  i.forEach((a) => s.set(a, ZD(e, a)));
                }
            }
            return t;
          })(t, d, l);
          const f = (function G2(e, t) {
            let n = null,
              r = null;
            return (
              Array.isArray(t) && t.length
                ? ((n = jh(t[0])), t.length > 1 && (r = jh(t[t.length - 1])))
                : t instanceof Map && (n = jh(t)),
              n || r ? new W2(e, n, r) : null
            );
          })(t, d);
          return new uw(t, d, c, f);
        }
      }
      let Q2 = (() => {
        class e extends OD {
          constructor(n, r) {
            super(),
              (this._nextAnimationId = 0),
              (this._renderer = n.createRenderer(r.body, {
                id: "0",
                encapsulation: It.None,
                styles: [],
                data: { animation: [] },
              }));
          }
          build(n) {
            const r = this._nextAnimationId.toString();
            this._nextAnimationId++;
            const i = Array.isArray(n) ? PD(n) : n;
            return (
              dw(this._renderer, null, r, "register", [i]),
              new Y2(r, this._renderer)
            );
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(Fo), D(ce));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      class Y2 extends dL {
        constructor(t, n) {
          super(), (this._id = t), (this._renderer = n);
        }
        create(t, n) {
          return new X2(this._id, t, n || {}, this._renderer);
        }
      }
      class X2 {
        constructor(t, n, r, i) {
          (this.id = t),
            (this.element = n),
            (this._renderer = i),
            (this.parentPlayer = null),
            (this._started = !1),
            (this.totalTime = 0),
            this._command("create", r);
        }
        _listen(t, n) {
          return this._renderer.listen(this.element, `@@${this.id}:${t}`, n);
        }
        _command(t, ...n) {
          return dw(this._renderer, this.element, this.id, t, n);
        }
        onDone(t) {
          this._listen("done", t);
        }
        onStart(t) {
          this._listen("start", t);
        }
        onDestroy(t) {
          this._listen("destroy", t);
        }
        init() {
          this._command("init");
        }
        hasStarted() {
          return this._started;
        }
        play() {
          this._command("play"), (this._started = !0);
        }
        pause() {
          this._command("pause");
        }
        restart() {
          this._command("restart");
        }
        finish() {
          this._command("finish");
        }
        destroy() {
          this._command("destroy");
        }
        reset() {
          this._command("reset"), (this._started = !1);
        }
        setPosition(t) {
          this._command("setPosition", t);
        }
        getPosition() {
          return this._renderer.engine.players[+this.id]?.getPosition() ?? 0;
        }
      }
      function dw(e, t, n, r, i) {
        return e.setProperty(t, `@@${n}:${r}`, i);
      }
      const fw = "@.disabled";
      let J2 = (() => {
        class e {
          constructor(n, r, i) {
            (this.delegate = n),
              (this.engine = r),
              (this._zone = i),
              (this._currentId = 0),
              (this._microtaskId = 1),
              (this._animationCallbacksBuffer = []),
              (this._rendererCache = new Map()),
              (this._cdRecurDepth = 0),
              (r.onRemovalComplete = (o, s) => {
                const a = s?.parentNode(o);
                a && s.removeChild(a, o);
              });
          }
          createRenderer(n, r) {
            const o = this.delegate.createRenderer(n, r);
            if (!(n && r && r.data && r.data.animation)) {
              let u = this._rendererCache.get(o);
              return (
                u ||
                  ((u = new hw("", o, this.engine, () =>
                    this._rendererCache.delete(o),
                  )),
                  this._rendererCache.set(o, u)),
                u
              );
            }
            const s = r.id,
              a = r.id + "-" + this._currentId;
            this._currentId++, this.engine.register(a, n);
            const c = (u) => {
              Array.isArray(u)
                ? u.forEach(c)
                : this.engine.registerTrigger(s, a, n, u.name, u);
            };
            return r.data.animation.forEach(c), new ej(this, a, o, this.engine);
          }
          begin() {
            this._cdRecurDepth++, this.delegate.begin && this.delegate.begin();
          }
          _scheduleCountTask() {
            queueMicrotask(() => {
              this._microtaskId++;
            });
          }
          scheduleListenerCallback(n, r, i) {
            n >= 0 && n < this._microtaskId
              ? this._zone.run(() => r(i))
              : (0 == this._animationCallbacksBuffer.length &&
                  queueMicrotask(() => {
                    this._zone.run(() => {
                      this._animationCallbacksBuffer.forEach((o) => {
                        const [s, a] = o;
                        s(a);
                      }),
                        (this._animationCallbacksBuffer = []);
                    });
                  }),
                this._animationCallbacksBuffer.push([r, i]));
          }
          end() {
            this._cdRecurDepth--,
              0 == this._cdRecurDepth &&
                this._zone.runOutsideAngular(() => {
                  this._scheduleCountTask(),
                    this.engine.flush(this._microtaskId);
                }),
              this.delegate.end && this.delegate.end();
          }
          whenRenderingDone() {
            return this.engine.whenRenderingDone();
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(Fo), D(qc), D(W));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      class hw {
        constructor(t, n, r, i) {
          (this.namespaceId = t),
            (this.delegate = n),
            (this.engine = r),
            (this._onDestroy = i);
        }
        get data() {
          return this.delegate.data;
        }
        destroyNode(t) {
          this.delegate.destroyNode?.(t);
        }
        destroy() {
          this.engine.destroy(this.namespaceId, this.delegate),
            this.engine.afterFlushAnimationsDone(() => {
              queueMicrotask(() => {
                this.delegate.destroy();
              });
            }),
            this._onDestroy?.();
        }
        createElement(t, n) {
          return this.delegate.createElement(t, n);
        }
        createComment(t) {
          return this.delegate.createComment(t);
        }
        createText(t) {
          return this.delegate.createText(t);
        }
        appendChild(t, n) {
          this.delegate.appendChild(t, n),
            this.engine.onInsert(this.namespaceId, n, t, !1);
        }
        insertBefore(t, n, r, i = !0) {
          this.delegate.insertBefore(t, n, r),
            this.engine.onInsert(this.namespaceId, n, t, i);
        }
        removeChild(t, n, r) {
          this.engine.onRemove(this.namespaceId, n, this.delegate);
        }
        selectRootElement(t, n) {
          return this.delegate.selectRootElement(t, n);
        }
        parentNode(t) {
          return this.delegate.parentNode(t);
        }
        nextSibling(t) {
          return this.delegate.nextSibling(t);
        }
        setAttribute(t, n, r, i) {
          this.delegate.setAttribute(t, n, r, i);
        }
        removeAttribute(t, n, r) {
          this.delegate.removeAttribute(t, n, r);
        }
        addClass(t, n) {
          this.delegate.addClass(t, n);
        }
        removeClass(t, n) {
          this.delegate.removeClass(t, n);
        }
        setStyle(t, n, r, i) {
          this.delegate.setStyle(t, n, r, i);
        }
        removeStyle(t, n, r) {
          this.delegate.removeStyle(t, n, r);
        }
        setProperty(t, n, r) {
          "@" == n.charAt(0) && n == fw
            ? this.disableAnimations(t, !!r)
            : this.delegate.setProperty(t, n, r);
        }
        setValue(t, n) {
          this.delegate.setValue(t, n);
        }
        listen(t, n, r) {
          return this.delegate.listen(t, n, r);
        }
        disableAnimations(t, n) {
          this.engine.disableAnimations(t, n);
        }
      }
      class ej extends hw {
        constructor(t, n, r, i, o) {
          super(n, r, i, o), (this.factory = t), (this.namespaceId = n);
        }
        setProperty(t, n, r) {
          "@" == n.charAt(0)
            ? "." == n.charAt(1) && n == fw
              ? this.disableAnimations(t, (r = void 0 === r || !!r))
              : this.engine.process(this.namespaceId, t, n.slice(1), r)
            : this.delegate.setProperty(t, n, r);
        }
        listen(t, n, r) {
          if ("@" == n.charAt(0)) {
            const i = (function tj(e) {
              switch (e) {
                case "body":
                  return document.body;
                case "document":
                  return document;
                case "window":
                  return window;
                default:
                  return e;
              }
            })(t);
            let o = n.slice(1),
              s = "";
            return (
              "@" != o.charAt(0) &&
                ([o, s] = (function nj(e) {
                  const t = e.indexOf(".");
                  return [e.substring(0, t), e.slice(t + 1)];
                })(o)),
              this.engine.listen(this.namespaceId, i, o, s, (a) => {
                this.factory.scheduleListenerCallback(a._data || -1, r, a);
              })
            );
          }
          return this.delegate.listen(t, n, r);
        }
      }
      const pw = [
          { provide: OD, useClass: Q2 },
          {
            provide: Rh,
            useFactory: function ij() {
              return new E2();
            },
          },
          {
            provide: qc,
            useClass: (() => {
              class e extends qc {
                constructor(n, r, i, o) {
                  super(n.body, r, i);
                }
                ngOnDestroy() {
                  this.flush();
                }
                static {
                  this.ɵfac = function (r) {
                    return new (r || e)(D(ce), D(Dh), D(Rh), D(_r));
                  };
                }
                static {
                  this.ɵprov = S({ token: e, factory: e.ɵfac });
                }
              }
              return e;
            })(),
          },
          {
            provide: Fo,
            useFactory: function oj(e, t, n) {
              return new J2(e, t, n);
            },
            deps: [dh, qc, W],
          },
        ],
        Bh = [
          { provide: Dh, useFactory: () => new Z2() },
          { provide: Oo, useValue: "BrowserAnimations" },
          ...pw,
        ],
        mw = [
          { provide: Dh, useClass: HD },
          { provide: Oo, useValue: "NoopAnimations" },
          ...pw,
        ];
      let sj = (() => {
        class e {
          static withConfig(n) {
            return { ngModule: e, providers: n.disableAnimations ? mw : Bh };
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵmod = Be({ type: e });
          }
          static {
            this.ɵinj = Ne({ providers: Bh, imports: [SD] });
          }
        }
        return e;
      })();
      function Li(e, t) {
        return ne(t) ? Ae(e, t, 1) : Ae(e, 1);
      }
      function Gt(e, t) {
        return De((n, r) => {
          let i = 0;
          n.subscribe(be(r, (o) => e.call(t, o, i++) && r.next(o)));
        });
      }
      function ji(e) {
        return De((t, n) => {
          try {
            t.subscribe(n);
          } finally {
            n.add(e);
          }
        });
      }
      class Wc {}
      class Kc {}
      class un {
        constructor(t) {
          (this.normalizedNames = new Map()),
            (this.lazyUpdate = null),
            t
              ? "string" == typeof t
                ? (this.lazyInit = () => {
                    (this.headers = new Map()),
                      t.split("\n").forEach((n) => {
                        const r = n.indexOf(":");
                        if (r > 0) {
                          const i = n.slice(0, r),
                            o = i.toLowerCase(),
                            s = n.slice(r + 1).trim();
                          this.maybeSetNormalizedName(i, o),
                            this.headers.has(o)
                              ? this.headers.get(o).push(s)
                              : this.headers.set(o, [s]);
                        }
                      });
                  })
                : typeof Headers < "u" && t instanceof Headers
                ? ((this.headers = new Map()),
                  t.forEach((n, r) => {
                    this.setHeaderEntries(r, n);
                  }))
                : (this.lazyInit = () => {
                    (this.headers = new Map()),
                      Object.entries(t).forEach(([n, r]) => {
                        this.setHeaderEntries(n, r);
                      });
                  })
              : (this.headers = new Map());
        }
        has(t) {
          return this.init(), this.headers.has(t.toLowerCase());
        }
        get(t) {
          this.init();
          const n = this.headers.get(t.toLowerCase());
          return n && n.length > 0 ? n[0] : null;
        }
        keys() {
          return this.init(), Array.from(this.normalizedNames.values());
        }
        getAll(t) {
          return this.init(), this.headers.get(t.toLowerCase()) || null;
        }
        append(t, n) {
          return this.clone({ name: t, value: n, op: "a" });
        }
        set(t, n) {
          return this.clone({ name: t, value: n, op: "s" });
        }
        delete(t, n) {
          return this.clone({ name: t, value: n, op: "d" });
        }
        maybeSetNormalizedName(t, n) {
          this.normalizedNames.has(n) || this.normalizedNames.set(n, t);
        }
        init() {
          this.lazyInit &&
            (this.lazyInit instanceof un
              ? this.copyFrom(this.lazyInit)
              : this.lazyInit(),
            (this.lazyInit = null),
            this.lazyUpdate &&
              (this.lazyUpdate.forEach((t) => this.applyUpdate(t)),
              (this.lazyUpdate = null)));
        }
        copyFrom(t) {
          t.init(),
            Array.from(t.headers.keys()).forEach((n) => {
              this.headers.set(n, t.headers.get(n)),
                this.normalizedNames.set(n, t.normalizedNames.get(n));
            });
        }
        clone(t) {
          const n = new un();
          return (
            (n.lazyInit =
              this.lazyInit && this.lazyInit instanceof un
                ? this.lazyInit
                : this),
            (n.lazyUpdate = (this.lazyUpdate || []).concat([t])),
            n
          );
        }
        applyUpdate(t) {
          const n = t.name.toLowerCase();
          switch (t.op) {
            case "a":
            case "s":
              let r = t.value;
              if (("string" == typeof r && (r = [r]), 0 === r.length)) return;
              this.maybeSetNormalizedName(t.name, n);
              const i = ("a" === t.op ? this.headers.get(n) : void 0) || [];
              i.push(...r), this.headers.set(n, i);
              break;
            case "d":
              const o = t.value;
              if (o) {
                let s = this.headers.get(n);
                if (!s) return;
                (s = s.filter((a) => -1 === o.indexOf(a))),
                  0 === s.length
                    ? (this.headers.delete(n), this.normalizedNames.delete(n))
                    : this.headers.set(n, s);
              } else this.headers.delete(n), this.normalizedNames.delete(n);
          }
        }
        setHeaderEntries(t, n) {
          const r = (Array.isArray(n) ? n : [n]).map((o) => o.toString()),
            i = t.toLowerCase();
          this.headers.set(i, r), this.maybeSetNormalizedName(t, i);
        }
        forEach(t) {
          this.init(),
            Array.from(this.normalizedNames.keys()).forEach((n) =>
              t(this.normalizedNames.get(n), this.headers.get(n)),
            );
        }
      }
      class aj {
        encodeKey(t) {
          return gw(t);
        }
        encodeValue(t) {
          return gw(t);
        }
        decodeKey(t) {
          return decodeURIComponent(t);
        }
        decodeValue(t) {
          return decodeURIComponent(t);
        }
      }
      const lj = /%(\d[a-f0-9])/gi,
        uj = {
          40: "@",
          "3A": ":",
          24: "$",
          "2C": ",",
          "3B": ";",
          "3D": "=",
          "3F": "?",
          "2F": "/",
        };
      function gw(e) {
        return encodeURIComponent(e).replace(lj, (t, n) => uj[n] ?? t);
      }
      function Zc(e) {
        return `${e}`;
      }
      class Yn {
        constructor(t = {}) {
          if (
            ((this.updates = null),
            (this.cloneFrom = null),
            (this.encoder = t.encoder || new aj()),
            t.fromString)
          ) {
            if (t.fromObject)
              throw new Error("Cannot specify both fromString and fromObject.");
            this.map = (function cj(e, t) {
              const n = new Map();
              return (
                e.length > 0 &&
                  e
                    .replace(/^\?/, "")
                    .split("&")
                    .forEach((i) => {
                      const o = i.indexOf("="),
                        [s, a] =
                          -1 == o
                            ? [t.decodeKey(i), ""]
                            : [
                                t.decodeKey(i.slice(0, o)),
                                t.decodeValue(i.slice(o + 1)),
                              ],
                        c = n.get(s) || [];
                      c.push(a), n.set(s, c);
                    }),
                n
              );
            })(t.fromString, this.encoder);
          } else
            t.fromObject
              ? ((this.map = new Map()),
                Object.keys(t.fromObject).forEach((n) => {
                  const r = t.fromObject[n],
                    i = Array.isArray(r) ? r.map(Zc) : [Zc(r)];
                  this.map.set(n, i);
                }))
              : (this.map = null);
        }
        has(t) {
          return this.init(), this.map.has(t);
        }
        get(t) {
          this.init();
          const n = this.map.get(t);
          return n ? n[0] : null;
        }
        getAll(t) {
          return this.init(), this.map.get(t) || null;
        }
        keys() {
          return this.init(), Array.from(this.map.keys());
        }
        append(t, n) {
          return this.clone({ param: t, value: n, op: "a" });
        }
        appendAll(t) {
          const n = [];
          return (
            Object.keys(t).forEach((r) => {
              const i = t[r];
              Array.isArray(i)
                ? i.forEach((o) => {
                    n.push({ param: r, value: o, op: "a" });
                  })
                : n.push({ param: r, value: i, op: "a" });
            }),
            this.clone(n)
          );
        }
        set(t, n) {
          return this.clone({ param: t, value: n, op: "s" });
        }
        delete(t, n) {
          return this.clone({ param: t, value: n, op: "d" });
        }
        toString() {
          return (
            this.init(),
            this.keys()
              .map((t) => {
                const n = this.encoder.encodeKey(t);
                return this.map
                  .get(t)
                  .map((r) => n + "=" + this.encoder.encodeValue(r))
                  .join("&");
              })
              .filter((t) => "" !== t)
              .join("&")
          );
        }
        clone(t) {
          const n = new Yn({ encoder: this.encoder });
          return (
            (n.cloneFrom = this.cloneFrom || this),
            (n.updates = (this.updates || []).concat(t)),
            n
          );
        }
        init() {
          null === this.map && (this.map = new Map()),
            null !== this.cloneFrom &&
              (this.cloneFrom.init(),
              this.cloneFrom
                .keys()
                .forEach((t) => this.map.set(t, this.cloneFrom.map.get(t))),
              this.updates.forEach((t) => {
                switch (t.op) {
                  case "a":
                  case "s":
                    const n =
                      ("a" === t.op ? this.map.get(t.param) : void 0) || [];
                    n.push(Zc(t.value)), this.map.set(t.param, n);
                    break;
                  case "d":
                    if (void 0 === t.value) {
                      this.map.delete(t.param);
                      break;
                    }
                    {
                      let r = this.map.get(t.param) || [];
                      const i = r.indexOf(Zc(t.value));
                      -1 !== i && r.splice(i, 1),
                        r.length > 0
                          ? this.map.set(t.param, r)
                          : this.map.delete(t.param);
                    }
                }
              }),
              (this.cloneFrom = this.updates = null));
        }
      }
      class dj {
        constructor() {
          this.map = new Map();
        }
        set(t, n) {
          return this.map.set(t, n), this;
        }
        get(t) {
          return (
            this.map.has(t) || this.map.set(t, t.defaultValue()),
            this.map.get(t)
          );
        }
        delete(t) {
          return this.map.delete(t), this;
        }
        has(t) {
          return this.map.has(t);
        }
        keys() {
          return this.map.keys();
        }
      }
      function bw(e) {
        return typeof ArrayBuffer < "u" && e instanceof ArrayBuffer;
      }
      function yw(e) {
        return typeof Blob < "u" && e instanceof Blob;
      }
      function vw(e) {
        return typeof FormData < "u" && e instanceof FormData;
      }
      class ms {
        constructor(t, n, r, i) {
          let o;
          if (
            ((this.url = n),
            (this.body = null),
            (this.reportProgress = !1),
            (this.withCredentials = !1),
            (this.responseType = "json"),
            (this.method = t.toUpperCase()),
            (function fj(e) {
              switch (e) {
                case "DELETE":
                case "GET":
                case "HEAD":
                case "OPTIONS":
                case "JSONP":
                  return !1;
                default:
                  return !0;
              }
            })(this.method) || i
              ? ((this.body = void 0 !== r ? r : null), (o = i))
              : (o = r),
            o &&
              ((this.reportProgress = !!o.reportProgress),
              (this.withCredentials = !!o.withCredentials),
              o.responseType && (this.responseType = o.responseType),
              o.headers && (this.headers = o.headers),
              o.context && (this.context = o.context),
              o.params && (this.params = o.params)),
            this.headers || (this.headers = new un()),
            this.context || (this.context = new dj()),
            this.params)
          ) {
            const s = this.params.toString();
            if (0 === s.length) this.urlWithParams = n;
            else {
              const a = n.indexOf("?");
              this.urlWithParams =
                n + (-1 === a ? "?" : a < n.length - 1 ? "&" : "") + s;
            }
          } else (this.params = new Yn()), (this.urlWithParams = n);
        }
        serializeBody() {
          return null === this.body
            ? null
            : bw(this.body) ||
              yw(this.body) ||
              vw(this.body) ||
              (function hj(e) {
                return (
                  typeof URLSearchParams < "u" && e instanceof URLSearchParams
                );
              })(this.body) ||
              "string" == typeof this.body
            ? this.body
            : this.body instanceof Yn
            ? this.body.toString()
            : "object" == typeof this.body ||
              "boolean" == typeof this.body ||
              Array.isArray(this.body)
            ? JSON.stringify(this.body)
            : this.body.toString();
        }
        detectContentTypeHeader() {
          return null === this.body || vw(this.body)
            ? null
            : yw(this.body)
            ? this.body.type || null
            : bw(this.body)
            ? null
            : "string" == typeof this.body
            ? "text/plain"
            : this.body instanceof Yn
            ? "application/x-www-form-urlencoded;charset=UTF-8"
            : "object" == typeof this.body ||
              "number" == typeof this.body ||
              "boolean" == typeof this.body
            ? "application/json"
            : null;
        }
        clone(t = {}) {
          const n = t.method || this.method,
            r = t.url || this.url,
            i = t.responseType || this.responseType,
            o = void 0 !== t.body ? t.body : this.body,
            s =
              void 0 !== t.withCredentials
                ? t.withCredentials
                : this.withCredentials,
            a =
              void 0 !== t.reportProgress
                ? t.reportProgress
                : this.reportProgress;
          let c = t.headers || this.headers,
            l = t.params || this.params;
          const u = t.context ?? this.context;
          return (
            void 0 !== t.setHeaders &&
              (c = Object.keys(t.setHeaders).reduce(
                (d, f) => d.set(f, t.setHeaders[f]),
                c,
              )),
            t.setParams &&
              (l = Object.keys(t.setParams).reduce(
                (d, f) => d.set(f, t.setParams[f]),
                l,
              )),
            new ms(n, r, o, {
              params: l,
              headers: c,
              context: u,
              reportProgress: a,
              responseType: i,
              withCredentials: s,
            })
          );
        }
      }
      var Bi = (function (e) {
        return (
          (e[(e.Sent = 0)] = "Sent"),
          (e[(e.UploadProgress = 1)] = "UploadProgress"),
          (e[(e.ResponseHeader = 2)] = "ResponseHeader"),
          (e[(e.DownloadProgress = 3)] = "DownloadProgress"),
          (e[(e.Response = 4)] = "Response"),
          (e[(e.User = 5)] = "User"),
          e
        );
      })(Bi || {});
      class Vh {
        constructor(t, n = 200, r = "OK") {
          (this.headers = t.headers || new un()),
            (this.status = void 0 !== t.status ? t.status : n),
            (this.statusText = t.statusText || r),
            (this.url = t.url || null),
            (this.ok = this.status >= 200 && this.status < 300);
        }
      }
      class $h extends Vh {
        constructor(t = {}) {
          super(t), (this.type = Bi.ResponseHeader);
        }
        clone(t = {}) {
          return new $h({
            headers: t.headers || this.headers,
            status: void 0 !== t.status ? t.status : this.status,
            statusText: t.statusText || this.statusText,
            url: t.url || this.url || void 0,
          });
        }
      }
      class Vi extends Vh {
        constructor(t = {}) {
          super(t),
            (this.type = Bi.Response),
            (this.body = void 0 !== t.body ? t.body : null);
        }
        clone(t = {}) {
          return new Vi({
            body: void 0 !== t.body ? t.body : this.body,
            headers: t.headers || this.headers,
            status: void 0 !== t.status ? t.status : this.status,
            statusText: t.statusText || this.statusText,
            url: t.url || this.url || void 0,
          });
        }
      }
      class _w extends Vh {
        constructor(t) {
          super(t, 0, "Unknown Error"),
            (this.name = "HttpErrorResponse"),
            (this.ok = !1),
            (this.message =
              this.status >= 200 && this.status < 300
                ? `Http failure during parsing for ${t.url || "(unknown url)"}`
                : `Http failure response for ${t.url || "(unknown url)"}: ${
                    t.status
                  } ${t.statusText}`),
            (this.error = t.error || null);
        }
      }
      function Uh(e, t) {
        return {
          body: t,
          headers: e.headers,
          context: e.context,
          observe: e.observe,
          params: e.params,
          reportProgress: e.reportProgress,
          responseType: e.responseType,
          withCredentials: e.withCredentials,
        };
      }
      let Qc = (() => {
        class e {
          constructor(n) {
            this.handler = n;
          }
          request(n, r, i = {}) {
            let o;
            if (n instanceof ms) o = n;
            else {
              let c, l;
              (c = i.headers instanceof un ? i.headers : new un(i.headers)),
                i.params &&
                  (l =
                    i.params instanceof Yn
                      ? i.params
                      : new Yn({ fromObject: i.params })),
                (o = new ms(n, r, void 0 !== i.body ? i.body : null, {
                  headers: c,
                  context: i.context,
                  params: l,
                  reportProgress: i.reportProgress,
                  responseType: i.responseType || "json",
                  withCredentials: i.withCredentials,
                }));
            }
            const s = A(o).pipe(Li((c) => this.handler.handle(c)));
            if (n instanceof ms || "events" === i.observe) return s;
            const a = s.pipe(Gt((c) => c instanceof Vi));
            switch (i.observe || "body") {
              case "body":
                switch (o.responseType) {
                  case "arraybuffer":
                    return a.pipe(
                      U((c) => {
                        if (null !== c.body && !(c.body instanceof ArrayBuffer))
                          throw new Error("Response is not an ArrayBuffer.");
                        return c.body;
                      }),
                    );
                  case "blob":
                    return a.pipe(
                      U((c) => {
                        if (null !== c.body && !(c.body instanceof Blob))
                          throw new Error("Response is not a Blob.");
                        return c.body;
                      }),
                    );
                  case "text":
                    return a.pipe(
                      U((c) => {
                        if (null !== c.body && "string" != typeof c.body)
                          throw new Error("Response is not a string.");
                        return c.body;
                      }),
                    );
                  default:
                    return a.pipe(U((c) => c.body));
                }
              case "response":
                return a;
              default:
                throw new Error(
                  `Unreachable: unhandled observe type ${i.observe}}`,
                );
            }
          }
          delete(n, r = {}) {
            return this.request("DELETE", n, r);
          }
          get(n, r = {}) {
            return this.request("GET", n, r);
          }
          head(n, r = {}) {
            return this.request("HEAD", n, r);
          }
          jsonp(n, r) {
            return this.request("JSONP", n, {
              params: new Yn().append(r, "JSONP_CALLBACK"),
              observe: "body",
              responseType: "json",
            });
          }
          options(n, r = {}) {
            return this.request("OPTIONS", n, r);
          }
          patch(n, r, i = {}) {
            return this.request("PATCH", n, Uh(i, r));
          }
          post(n, r, i = {}) {
            return this.request("POST", n, Uh(i, r));
          }
          put(n, r, i = {}) {
            return this.request("PUT", n, Uh(i, r));
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(Wc));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      function Ew(e, t) {
        return t(e);
      }
      function mj(e, t) {
        return (n, r) => t.intercept(n, { handle: (i) => e(i, r) });
      }
      const bj = new E(""),
        gs = new E(""),
        Cw = new E("");
      function yj() {
        let e = null;
        return (t, n) => {
          null === e &&
            (e = (C(bj, { optional: !0 }) ?? []).reduceRight(mj, Ew));
          const r = C(fc),
            i = r.add();
          return e(t, n).pipe(ji(() => r.remove(i)));
        };
      }
      let Iw = (() => {
        class e extends Wc {
          constructor(n, r) {
            super(),
              (this.backend = n),
              (this.injector = r),
              (this.chain = null),
              (this.pendingTasks = C(fc));
          }
          handle(n) {
            if (null === this.chain) {
              const i = Array.from(
                new Set([
                  ...this.injector.get(gs),
                  ...this.injector.get(Cw, []),
                ]),
              );
              this.chain = i.reduceRight(
                (o, s) =>
                  (function gj(e, t, n) {
                    return (r, i) => n.runInContext(() => t(r, (o) => e(o, i)));
                  })(o, s, this.injector),
                Ew,
              );
            }
            const r = this.pendingTasks.add();
            return this.chain(n, (i) => this.backend.handle(i)).pipe(
              ji(() => this.pendingTasks.remove(r)),
            );
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(Kc), D(mt));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      const wj = /^\)\]\}',?\n/;
      let Sw = (() => {
        class e {
          constructor(n) {
            this.xhrFactory = n;
          }
          handle(n) {
            if ("JSONP" === n.method) throw new v(-2800, !1);
            const r = this.xhrFactory;
            return (r.ɵloadImpl ? Se(r.ɵloadImpl()) : A(null)).pipe(
              Ft(
                () =>
                  new pe((o) => {
                    const s = r.build();
                    if (
                      (s.open(n.method, n.urlWithParams),
                      n.withCredentials && (s.withCredentials = !0),
                      n.headers.forEach((m, g) =>
                        s.setRequestHeader(m, g.join(",")),
                      ),
                      n.headers.has("Accept") ||
                        s.setRequestHeader(
                          "Accept",
                          "application/json, text/plain, */*",
                        ),
                      !n.headers.has("Content-Type"))
                    ) {
                      const m = n.detectContentTypeHeader();
                      null !== m && s.setRequestHeader("Content-Type", m);
                    }
                    if (n.responseType) {
                      const m = n.responseType.toLowerCase();
                      s.responseType = "json" !== m ? m : "text";
                    }
                    const a = n.serializeBody();
                    let c = null;
                    const l = () => {
                        if (null !== c) return c;
                        const m = s.statusText || "OK",
                          g = new un(s.getAllResponseHeaders()),
                          y =
                            (function Ej(e) {
                              return "responseURL" in e && e.responseURL
                                ? e.responseURL
                                : /^X-Request-URL:/m.test(
                                    e.getAllResponseHeaders(),
                                  )
                                ? e.getResponseHeader("X-Request-URL")
                                : null;
                            })(s) || n.url;
                        return (
                          (c = new $h({
                            headers: g,
                            status: s.status,
                            statusText: m,
                            url: y,
                          })),
                          c
                        );
                      },
                      u = () => {
                        let {
                            headers: m,
                            status: g,
                            statusText: y,
                            url: b,
                          } = l(),
                          w = null;
                        204 !== g &&
                          (w =
                            typeof s.response > "u"
                              ? s.responseText
                              : s.response),
                          0 === g && (g = w ? 200 : 0);
                        let M = g >= 200 && g < 300;
                        if ("json" === n.responseType && "string" == typeof w) {
                          const F = w;
                          w = w.replace(wj, "");
                          try {
                            w = "" !== w ? JSON.parse(w) : null;
                          } catch (te) {
                            (w = F),
                              M && ((M = !1), (w = { error: te, text: w }));
                          }
                        }
                        M
                          ? (o.next(
                              new Vi({
                                body: w,
                                headers: m,
                                status: g,
                                statusText: y,
                                url: b || void 0,
                              }),
                            ),
                            o.complete())
                          : o.error(
                              new _w({
                                error: w,
                                headers: m,
                                status: g,
                                statusText: y,
                                url: b || void 0,
                              }),
                            );
                      },
                      d = (m) => {
                        const { url: g } = l(),
                          y = new _w({
                            error: m,
                            status: s.status || 0,
                            statusText: s.statusText || "Unknown Error",
                            url: g || void 0,
                          });
                        o.error(y);
                      };
                    let f = !1;
                    const h = (m) => {
                        f || (o.next(l()), (f = !0));
                        let g = { type: Bi.DownloadProgress, loaded: m.loaded };
                        m.lengthComputable && (g.total = m.total),
                          "text" === n.responseType &&
                            s.responseText &&
                            (g.partialText = s.responseText),
                          o.next(g);
                      },
                      p = (m) => {
                        let g = { type: Bi.UploadProgress, loaded: m.loaded };
                        m.lengthComputable && (g.total = m.total), o.next(g);
                      };
                    return (
                      s.addEventListener("load", u),
                      s.addEventListener("error", d),
                      s.addEventListener("timeout", d),
                      s.addEventListener("abort", d),
                      n.reportProgress &&
                        (s.addEventListener("progress", h),
                        null !== a &&
                          s.upload &&
                          s.upload.addEventListener("progress", p)),
                      s.send(a),
                      o.next({ type: Bi.Sent }),
                      () => {
                        s.removeEventListener("error", d),
                          s.removeEventListener("abort", d),
                          s.removeEventListener("load", u),
                          s.removeEventListener("timeout", d),
                          n.reportProgress &&
                            (s.removeEventListener("progress", h),
                            null !== a &&
                              s.upload &&
                              s.upload.removeEventListener("progress", p)),
                          s.readyState !== s.DONE && s.abort();
                      }
                    );
                  }),
              ),
            );
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(uD));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      const Hh = new E("XSRF_ENABLED"),
        xw = new E("XSRF_COOKIE_NAME", {
          providedIn: "root",
          factory: () => "XSRF-TOKEN",
        }),
        Tw = new E("XSRF_HEADER_NAME", {
          providedIn: "root",
          factory: () => "X-XSRF-TOKEN",
        });
      class Aw {}
      let Mj = (() => {
        class e {
          constructor(n, r, i) {
            (this.doc = n),
              (this.platform = r),
              (this.cookieName = i),
              (this.lastCookieString = ""),
              (this.lastToken = null),
              (this.parseCount = 0);
          }
          getToken() {
            if ("server" === this.platform) return null;
            const n = this.doc.cookie || "";
            return (
              n !== this.lastCookieString &&
                (this.parseCount++,
                (this.lastToken = J0(n, this.cookieName)),
                (this.lastCookieString = n)),
              this.lastToken
            );
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(ce), D(zn), D(xw));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      function Sj(e, t) {
        const n = e.url.toLowerCase();
        if (
          !C(Hh) ||
          "GET" === e.method ||
          "HEAD" === e.method ||
          n.startsWith("http://") ||
          n.startsWith("https://")
        )
          return t(e);
        const r = C(Aw).getToken(),
          i = C(Tw);
        return (
          null != r &&
            !e.headers.has(i) &&
            (e = e.clone({ headers: e.headers.set(i, r) })),
          t(e)
        );
      }
      var Xn = (function (e) {
        return (
          (e[(e.Interceptors = 0)] = "Interceptors"),
          (e[(e.LegacyInterceptors = 1)] = "LegacyInterceptors"),
          (e[(e.CustomXsrfConfiguration = 2)] = "CustomXsrfConfiguration"),
          (e[(e.NoXsrfProtection = 3)] = "NoXsrfProtection"),
          (e[(e.JsonpSupport = 4)] = "JsonpSupport"),
          (e[(e.RequestsMadeViaParent = 5)] = "RequestsMadeViaParent"),
          (e[(e.Fetch = 6)] = "Fetch"),
          e
        );
      })(Xn || {});
      function Mr(e, t) {
        return { ɵkind: e, ɵproviders: t };
      }
      function xj(...e) {
        const t = [
          Qc,
          Sw,
          Iw,
          { provide: Wc, useExisting: Iw },
          { provide: Kc, useExisting: Sw },
          { provide: gs, useValue: Sj, multi: !0 },
          { provide: Hh, useValue: !0 },
          { provide: Aw, useClass: Mj },
        ];
        for (const n of e) t.push(...n.ɵproviders);
        return (function ed(e) {
          return { ɵproviders: e };
        })(t);
      }
      const Nw = new E("LEGACY_INTERCEPTOR_FN");
      let Aj = (() => {
        class e {
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵmod = Be({ type: e });
          }
          static {
            this.ɵinj = Ne({
              providers: [
                xj(
                  Mr(Xn.LegacyInterceptors, [
                    { provide: Nw, useFactory: yj },
                    { provide: gs, useExisting: Nw, multi: !0 },
                  ]),
                ),
              ],
            });
          }
        }
        return e;
      })();
      const { isArray: Lj } = Array,
        { getPrototypeOf: jj, prototype: Bj, keys: Vj } = Object;
      function Rw(e) {
        if (1 === e.length) {
          const t = e[0];
          if (Lj(t)) return { args: t, keys: null };
          if (
            (function $j(e) {
              return e && "object" == typeof e && jj(e) === Bj;
            })(t)
          ) {
            const n = Vj(t);
            return { args: n.map((r) => t[r]), keys: n };
          }
        }
        return { args: e, keys: null };
      }
      const { isArray: Uj } = Array;
      function Ow(e) {
        return U((t) =>
          (function Hj(e, t) {
            return Uj(t) ? e(...t) : e(t);
          })(e, t),
        );
      }
      function Pw(e, t) {
        return e.reduce((n, r, i) => ((n[r] = t[i]), n), {});
      }
      function Xc(...e) {
        const t = no(e),
          n = Hp(e),
          { args: r, keys: i } = Rw(e);
        if (0 === r.length) return Se([], t);
        const o = new pe(
          (function zj(e, t, n = kn) {
            return (r) => {
              kw(
                t,
                () => {
                  const { length: i } = e,
                    o = new Array(i);
                  let s = i,
                    a = i;
                  for (let c = 0; c < i; c++)
                    kw(
                      t,
                      () => {
                        const l = Se(e[c], t);
                        let u = !1;
                        l.subscribe(
                          be(
                            r,
                            (d) => {
                              (o[c] = d),
                                u || ((u = !0), a--),
                                a || r.next(n(o.slice()));
                            },
                            () => {
                              --s || r.complete();
                            },
                          ),
                        );
                      },
                      r,
                    );
                },
                r,
              );
            };
          })(r, t, i ? (s) => Pw(i, s) : kn),
        );
        return n ? o.pipe(Ow(n)) : o;
      }
      function kw(e, t, n) {
        e ? pn(n, e, t) : t();
      }
      const Jc = eo(
        (e) =>
          function () {
            e(this),
              (this.name = "EmptyError"),
              (this.message = "no elements in sequence");
          },
      );
      function el(...e) {
        return (function qj() {
          return Lr(1);
        })()(Se(e, no(e)));
      }
      function Fw(e) {
        return new pe((t) => {
          ct(e()).subscribe(t);
        });
      }
      function $i(e, t) {
        const n = ne(e) ? e : () => e,
          r = (i) => i.error(n());
        return new pe(t ? (i) => t.schedule(r, 0, i) : r);
      }
      function zh() {
        return De((e, t) => {
          let n = null;
          e._refCount++;
          const r = be(t, void 0, void 0, void 0, () => {
            if (!e || e._refCount <= 0 || 0 < --e._refCount)
              return void (n = null);
            const i = e._connection,
              o = n;
            (n = null),
              i && (!o || i === o) && i.unsubscribe(),
              t.unsubscribe();
          });
          e.subscribe(r), r.closed || (n = e.connect());
        });
      }
      class Lw extends pe {
        constructor(t, n) {
          super(),
            (this.source = t),
            (this.subjectFactory = n),
            (this._subject = null),
            (this._refCount = 0),
            (this._connection = null),
            xp(t) && (this.lift = t.lift);
        }
        _subscribe(t) {
          return this.getSubject().subscribe(t);
        }
        getSubject() {
          const t = this._subject;
          return (
            (!t || t.isStopped) && (this._subject = this.subjectFactory()),
            this._subject
          );
        }
        _teardown() {
          this._refCount = 0;
          const { _connection: t } = this;
          (this._subject = this._connection = null), t?.unsubscribe();
        }
        connect() {
          let t = this._connection;
          if (!t) {
            t = this._connection = new je();
            const n = this.getSubject();
            t.add(
              this.source.subscribe(
                be(
                  n,
                  void 0,
                  () => {
                    this._teardown(), n.complete();
                  },
                  (r) => {
                    this._teardown(), n.error(r);
                  },
                  () => this._teardown(),
                ),
              ),
            ),
              t.closed && ((this._connection = null), (t = je.EMPTY));
          }
          return t;
        }
        refCount() {
          return zh()(this);
        }
      }
      function Nn(e) {
        return e <= 0
          ? () => Zt
          : De((t, n) => {
              let r = 0;
              t.subscribe(
                be(n, (i) => {
                  ++r <= e && (n.next(i), e <= r && n.complete());
                }),
              );
            });
      }
      function jw(...e) {
        const t = no(e);
        return De((n, r) => {
          (t ? el(e, n, t) : el(e, n)).subscribe(r);
        });
      }
      function tl(e) {
        return De((t, n) => {
          let r = !1;
          t.subscribe(
            be(
              n,
              (i) => {
                (r = !0), n.next(i);
              },
              () => {
                r || n.next(e), n.complete();
              },
            ),
          );
        });
      }
      function Bw(e = Gj) {
        return De((t, n) => {
          let r = !1;
          t.subscribe(
            be(
              n,
              (i) => {
                (r = !0), n.next(i);
              },
              () => (r ? n.complete() : n.error(e())),
            ),
          );
        });
      }
      function Gj() {
        return new Jc();
      }
      function Sr(e, t) {
        const n = arguments.length >= 2;
        return (r) =>
          r.pipe(
            e ? Gt((i, o) => e(i, o, r)) : kn,
            Nn(1),
            n ? tl(t) : Bw(() => new Jc()),
          );
      }
      function Ee(e, t, n) {
        const r = ne(e) || t || n ? { next: e, error: t, complete: n } : e;
        return r
          ? De((i, o) => {
              var s;
              null === (s = r.subscribe) || void 0 === s || s.call(r);
              let a = !0;
              i.subscribe(
                be(
                  o,
                  (c) => {
                    var l;
                    null === (l = r.next) || void 0 === l || l.call(r, c),
                      o.next(c);
                  },
                  () => {
                    var c;
                    (a = !1),
                      null === (c = r.complete) || void 0 === c || c.call(r),
                      o.complete();
                  },
                  (c) => {
                    var l;
                    (a = !1),
                      null === (l = r.error) || void 0 === l || l.call(r, c),
                      o.error(c);
                  },
                  () => {
                    var c, l;
                    a &&
                      (null === (c = r.unsubscribe) ||
                        void 0 === c ||
                        c.call(r)),
                      null === (l = r.finalize) || void 0 === l || l.call(r);
                  },
                ),
              );
            })
          : kn;
      }
      function Jn(e) {
        return De((t, n) => {
          let o,
            r = null,
            i = !1;
          (r = t.subscribe(
            be(n, void 0, void 0, (s) => {
              (o = ct(e(s, Jn(e)(t)))),
                r ? (r.unsubscribe(), (r = null), o.subscribe(n)) : (i = !0);
            }),
          )),
            i && (r.unsubscribe(), (r = null), o.subscribe(n));
        });
      }
      function qh(e) {
        return e <= 0
          ? () => Zt
          : De((t, n) => {
              let r = [];
              t.subscribe(
                be(
                  n,
                  (i) => {
                    r.push(i), e < r.length && r.shift();
                  },
                  () => {
                    for (const i of r) n.next(i);
                    n.complete();
                  },
                  void 0,
                  () => {
                    r = null;
                  },
                ),
              );
            });
      }
      function Gh(e) {
        return De((t, n) => {
          ct(e).subscribe(be(n, () => n.complete(), Tl)),
            !n.closed && t.subscribe(n);
        });
      }
      const $ = "primary",
        bs = Symbol("RouteTitle");
      class Yj {
        constructor(t) {
          this.params = t || {};
        }
        has(t) {
          return Object.prototype.hasOwnProperty.call(this.params, t);
        }
        get(t) {
          if (this.has(t)) {
            const n = this.params[t];
            return Array.isArray(n) ? n[0] : n;
          }
          return null;
        }
        getAll(t) {
          if (this.has(t)) {
            const n = this.params[t];
            return Array.isArray(n) ? n : [n];
          }
          return [];
        }
        get keys() {
          return Object.keys(this.params);
        }
      }
      function Ui(e) {
        return new Yj(e);
      }
      function Xj(e, t, n) {
        const r = n.path.split("/");
        if (
          r.length > e.length ||
          ("full" === n.pathMatch && (t.hasChildren() || r.length < e.length))
        )
          return null;
        const i = {};
        for (let o = 0; o < r.length; o++) {
          const s = r[o],
            a = e[o];
          if (s.startsWith(":")) i[s.substring(1)] = a;
          else if (s !== a.path) return null;
        }
        return { consumed: e.slice(0, r.length), posParams: i };
      }
      function dn(e, t) {
        const n = e ? Object.keys(e) : void 0,
          r = t ? Object.keys(t) : void 0;
        if (!n || !r || n.length != r.length) return !1;
        let i;
        for (let o = 0; o < n.length; o++)
          if (((i = n[o]), !Vw(e[i], t[i]))) return !1;
        return !0;
      }
      function Vw(e, t) {
        if (Array.isArray(e) && Array.isArray(t)) {
          if (e.length !== t.length) return !1;
          const n = [...e].sort(),
            r = [...t].sort();
          return n.every((i, o) => r[o] === i);
        }
        return e === t;
      }
      function $w(e) {
        return e.length > 0 ? e[e.length - 1] : null;
      }
      function er(e) {
        return (function Fj(e) {
          return !!e && (e instanceof pe || (ne(e.lift) && ne(e.subscribe)));
        })(e)
          ? e
          : tc(e)
          ? Se(Promise.resolve(e))
          : A(e);
      }
      const eB = {
          exact: function zw(e, t, n) {
            if (
              !xr(e.segments, t.segments) ||
              !nl(e.segments, t.segments, n) ||
              e.numberOfChildren !== t.numberOfChildren
            )
              return !1;
            for (const r in t.children)
              if (!e.children[r] || !zw(e.children[r], t.children[r], n))
                return !1;
            return !0;
          },
          subset: qw,
        },
        Uw = {
          exact: function tB(e, t) {
            return dn(e, t);
          },
          subset: function nB(e, t) {
            return (
              Object.keys(t).length <= Object.keys(e).length &&
              Object.keys(t).every((n) => Vw(e[n], t[n]))
            );
          },
          ignored: () => !0,
        };
      function Hw(e, t, n) {
        return (
          eB[n.paths](e.root, t.root, n.matrixParams) &&
          Uw[n.queryParams](e.queryParams, t.queryParams) &&
          !("exact" === n.fragment && e.fragment !== t.fragment)
        );
      }
      function qw(e, t, n) {
        return Gw(e, t, t.segments, n);
      }
      function Gw(e, t, n, r) {
        if (e.segments.length > n.length) {
          const i = e.segments.slice(0, n.length);
          return !(!xr(i, n) || t.hasChildren() || !nl(i, n, r));
        }
        if (e.segments.length === n.length) {
          if (!xr(e.segments, n) || !nl(e.segments, n, r)) return !1;
          for (const i in t.children)
            if (!e.children[i] || !qw(e.children[i], t.children[i], r))
              return !1;
          return !0;
        }
        {
          const i = n.slice(0, e.segments.length),
            o = n.slice(e.segments.length);
          return (
            !!(xr(e.segments, i) && nl(e.segments, i, r) && e.children[$]) &&
            Gw(e.children[$], t, o, r)
          );
        }
      }
      function nl(e, t, n) {
        return t.every((r, i) => Uw[n](e[i].parameters, r.parameters));
      }
      class Hi {
        constructor(t = new ee([], {}), n = {}, r = null) {
          (this.root = t), (this.queryParams = n), (this.fragment = r);
        }
        get queryParamMap() {
          return (
            this._queryParamMap || (this._queryParamMap = Ui(this.queryParams)),
            this._queryParamMap
          );
        }
        toString() {
          return oB.serialize(this);
        }
      }
      class ee {
        constructor(t, n) {
          (this.segments = t),
            (this.children = n),
            (this.parent = null),
            Object.values(n).forEach((r) => (r.parent = this));
        }
        hasChildren() {
          return this.numberOfChildren > 0;
        }
        get numberOfChildren() {
          return Object.keys(this.children).length;
        }
        toString() {
          return rl(this);
        }
      }
      class ys {
        constructor(t, n) {
          (this.path = t), (this.parameters = n);
        }
        get parameterMap() {
          return (
            this._parameterMap || (this._parameterMap = Ui(this.parameters)),
            this._parameterMap
          );
        }
        toString() {
          return Zw(this);
        }
      }
      function xr(e, t) {
        return e.length === t.length && e.every((n, r) => n.path === t[r].path);
      }
      let vs = (() => {
        class e {
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({
              token: e,
              factory: function () {
                return new Wh();
              },
              providedIn: "root",
            });
          }
        }
        return e;
      })();
      class Wh {
        parse(t) {
          const n = new gB(t);
          return new Hi(
            n.parseRootSegment(),
            n.parseQueryParams(),
            n.parseFragment(),
          );
        }
        serialize(t) {
          const n = `/${_s(t.root, !0)}`,
            r = (function cB(e) {
              const t = Object.keys(e)
                .map((n) => {
                  const r = e[n];
                  return Array.isArray(r)
                    ? r.map((i) => `${il(n)}=${il(i)}`).join("&")
                    : `${il(n)}=${il(r)}`;
                })
                .filter((n) => !!n);
              return t.length ? `?${t.join("&")}` : "";
            })(t.queryParams);
          return `${n}${r}${
            "string" == typeof t.fragment
              ? `#${(function sB(e) {
                  return encodeURI(e);
                })(t.fragment)}`
              : ""
          }`;
        }
      }
      const oB = new Wh();
      function rl(e) {
        return e.segments.map((t) => Zw(t)).join("/");
      }
      function _s(e, t) {
        if (!e.hasChildren()) return rl(e);
        if (t) {
          const n = e.children[$] ? _s(e.children[$], !1) : "",
            r = [];
          return (
            Object.entries(e.children).forEach(([i, o]) => {
              i !== $ && r.push(`${i}:${_s(o, !1)}`);
            }),
            r.length > 0 ? `${n}(${r.join("//")})` : n
          );
        }
        {
          const n = (function iB(e, t) {
            let n = [];
            return (
              Object.entries(e.children).forEach(([r, i]) => {
                r === $ && (n = n.concat(t(i, r)));
              }),
              Object.entries(e.children).forEach(([r, i]) => {
                r !== $ && (n = n.concat(t(i, r)));
              }),
              n
            );
          })(e, (r, i) =>
            i === $ ? [_s(e.children[$], !1)] : [`${i}:${_s(r, !1)}`],
          );
          return 1 === Object.keys(e.children).length && null != e.children[$]
            ? `${rl(e)}/${n[0]}`
            : `${rl(e)}/(${n.join("//")})`;
        }
      }
      function Ww(e) {
        return encodeURIComponent(e)
          .replace(/%40/g, "@")
          .replace(/%3A/gi, ":")
          .replace(/%24/g, "$")
          .replace(/%2C/gi, ",");
      }
      function il(e) {
        return Ww(e).replace(/%3B/gi, ";");
      }
      function Kh(e) {
        return Ww(e)
          .replace(/\(/g, "%28")
          .replace(/\)/g, "%29")
          .replace(/%26/gi, "&");
      }
      function ol(e) {
        return decodeURIComponent(e);
      }
      function Kw(e) {
        return ol(e.replace(/\+/g, "%20"));
      }
      function Zw(e) {
        return `${Kh(e.path)}${(function aB(e) {
          return Object.keys(e)
            .map((t) => `;${Kh(t)}=${Kh(e[t])}`)
            .join("");
        })(e.parameters)}`;
      }
      const lB = /^[^\/()?;#]+/;
      function Zh(e) {
        const t = e.match(lB);
        return t ? t[0] : "";
      }
      const uB = /^[^\/()?;=#]+/,
        fB = /^[^=?&#]+/,
        pB = /^[^&#]+/;
      class gB {
        constructor(t) {
          (this.url = t), (this.remaining = t);
        }
        parseRootSegment() {
          return (
            this.consumeOptional("/"),
            "" === this.remaining ||
            this.peekStartsWith("?") ||
            this.peekStartsWith("#")
              ? new ee([], {})
              : new ee([], this.parseChildren())
          );
        }
        parseQueryParams() {
          const t = {};
          if (this.consumeOptional("?"))
            do {
              this.parseQueryParam(t);
            } while (this.consumeOptional("&"));
          return t;
        }
        parseFragment() {
          return this.consumeOptional("#")
            ? decodeURIComponent(this.remaining)
            : null;
        }
        parseChildren() {
          if ("" === this.remaining) return {};
          this.consumeOptional("/");
          const t = [];
          for (
            this.peekStartsWith("(") || t.push(this.parseSegment());
            this.peekStartsWith("/") &&
            !this.peekStartsWith("//") &&
            !this.peekStartsWith("/(");

          )
            this.capture("/"), t.push(this.parseSegment());
          let n = {};
          this.peekStartsWith("/(") &&
            (this.capture("/"), (n = this.parseParens(!0)));
          let r = {};
          return (
            this.peekStartsWith("(") && (r = this.parseParens(!1)),
            (t.length > 0 || Object.keys(n).length > 0) &&
              (r[$] = new ee(t, n)),
            r
          );
        }
        parseSegment() {
          const t = Zh(this.remaining);
          if ("" === t && this.peekStartsWith(";")) throw new v(4009, !1);
          return this.capture(t), new ys(ol(t), this.parseMatrixParams());
        }
        parseMatrixParams() {
          const t = {};
          for (; this.consumeOptional(";"); ) this.parseParam(t);
          return t;
        }
        parseParam(t) {
          const n = (function dB(e) {
            const t = e.match(uB);
            return t ? t[0] : "";
          })(this.remaining);
          if (!n) return;
          this.capture(n);
          let r = "";
          if (this.consumeOptional("=")) {
            const i = Zh(this.remaining);
            i && ((r = i), this.capture(r));
          }
          t[ol(n)] = ol(r);
        }
        parseQueryParam(t) {
          const n = (function hB(e) {
            const t = e.match(fB);
            return t ? t[0] : "";
          })(this.remaining);
          if (!n) return;
          this.capture(n);
          let r = "";
          if (this.consumeOptional("=")) {
            const s = (function mB(e) {
              const t = e.match(pB);
              return t ? t[0] : "";
            })(this.remaining);
            s && ((r = s), this.capture(r));
          }
          const i = Kw(n),
            o = Kw(r);
          if (t.hasOwnProperty(i)) {
            let s = t[i];
            Array.isArray(s) || ((s = [s]), (t[i] = s)), s.push(o);
          } else t[i] = o;
        }
        parseParens(t) {
          const n = {};
          for (
            this.capture("(");
            !this.consumeOptional(")") && this.remaining.length > 0;

          ) {
            const r = Zh(this.remaining),
              i = this.remaining[r.length];
            if ("/" !== i && ")" !== i && ";" !== i) throw new v(4010, !1);
            let o;
            r.indexOf(":") > -1
              ? ((o = r.slice(0, r.indexOf(":"))),
                this.capture(o),
                this.capture(":"))
              : t && (o = $);
            const s = this.parseChildren();
            (n[o] = 1 === Object.keys(s).length ? s[$] : new ee([], s)),
              this.consumeOptional("//");
          }
          return n;
        }
        peekStartsWith(t) {
          return this.remaining.startsWith(t);
        }
        consumeOptional(t) {
          return (
            !!this.peekStartsWith(t) &&
            ((this.remaining = this.remaining.substring(t.length)), !0)
          );
        }
        capture(t) {
          if (!this.consumeOptional(t)) throw new v(4011, !1);
        }
      }
      function Qw(e) {
        return e.segments.length > 0 ? new ee([], { [$]: e }) : e;
      }
      function Yw(e) {
        const t = {};
        for (const r of Object.keys(e.children)) {
          const o = Yw(e.children[r]);
          if (r === $ && 0 === o.segments.length && o.hasChildren())
            for (const [s, a] of Object.entries(o.children)) t[s] = a;
          else (o.segments.length > 0 || o.hasChildren()) && (t[r] = o);
        }
        return (function bB(e) {
          if (1 === e.numberOfChildren && e.children[$]) {
            const t = e.children[$];
            return new ee(e.segments.concat(t.segments), t.children);
          }
          return e;
        })(new ee(e.segments, t));
      }
      function Tr(e) {
        return e instanceof Hi;
      }
      function Xw(e) {
        let t;
        const i = Qw(
          (function n(o) {
            const s = {};
            for (const c of o.children) {
              const l = n(c);
              s[c.outlet] = l;
            }
            const a = new ee(o.url, s);
            return o === e && (t = a), a;
          })(e.root),
        );
        return t ?? i;
      }
      function Jw(e, t, n, r) {
        let i = e;
        for (; i.parent; ) i = i.parent;
        if (0 === t.length) return Qh(i, i, i, n, r);
        const o = (function vB(e) {
          if ("string" == typeof e[0] && 1 === e.length && "/" === e[0])
            return new tE(!0, 0, e);
          let t = 0,
            n = !1;
          const r = e.reduce((i, o, s) => {
            if ("object" == typeof o && null != o) {
              if (o.outlets) {
                const a = {};
                return (
                  Object.entries(o.outlets).forEach(([c, l]) => {
                    a[c] = "string" == typeof l ? l.split("/") : l;
                  }),
                  [...i, { outlets: a }]
                );
              }
              if (o.segmentPath) return [...i, o.segmentPath];
            }
            return "string" != typeof o
              ? [...i, o]
              : 0 === s
              ? (o.split("/").forEach((a, c) => {
                  (0 == c && "." === a) ||
                    (0 == c && "" === a
                      ? (n = !0)
                      : ".." === a
                      ? t++
                      : "" != a && i.push(a));
                }),
                i)
              : [...i, o];
          }, []);
          return new tE(n, t, r);
        })(t);
        if (o.toRoot()) return Qh(i, i, new ee([], {}), n, r);
        const s = (function _B(e, t, n) {
            if (e.isAbsolute) return new al(t, !0, 0);
            if (!n) return new al(t, !1, NaN);
            if (null === n.parent) return new al(n, !0, 0);
            const r = sl(e.commands[0]) ? 0 : 1;
            return (function DB(e, t, n) {
              let r = e,
                i = t,
                o = n;
              for (; o > i; ) {
                if (((o -= i), (r = r.parent), !r)) throw new v(4005, !1);
                i = r.segments.length;
              }
              return new al(r, !1, i - o);
            })(n, n.segments.length - 1 + r, e.numberOfDoubleDots);
          })(o, i, e),
          a = s.processChildren
            ? ws(s.segmentGroup, s.index, o.commands)
            : nE(s.segmentGroup, s.index, o.commands);
        return Qh(i, s.segmentGroup, a, n, r);
      }
      function sl(e) {
        return (
          "object" == typeof e && null != e && !e.outlets && !e.segmentPath
        );
      }
      function Ds(e) {
        return "object" == typeof e && null != e && e.outlets;
      }
      function Qh(e, t, n, r, i) {
        let s,
          o = {};
        r &&
          Object.entries(r).forEach(([c, l]) => {
            o[c] = Array.isArray(l) ? l.map((u) => `${u}`) : `${l}`;
          }),
          (s = e === t ? n : eE(e, t, n));
        const a = Qw(Yw(s));
        return new Hi(a, o, i);
      }
      function eE(e, t, n) {
        const r = {};
        return (
          Object.entries(e.children).forEach(([i, o]) => {
            r[i] = o === t ? n : eE(o, t, n);
          }),
          new ee(e.segments, r)
        );
      }
      class tE {
        constructor(t, n, r) {
          if (
            ((this.isAbsolute = t),
            (this.numberOfDoubleDots = n),
            (this.commands = r),
            t && r.length > 0 && sl(r[0]))
          )
            throw new v(4003, !1);
          const i = r.find(Ds);
          if (i && i !== $w(r)) throw new v(4004, !1);
        }
        toRoot() {
          return (
            this.isAbsolute &&
            1 === this.commands.length &&
            "/" == this.commands[0]
          );
        }
      }
      class al {
        constructor(t, n, r) {
          (this.segmentGroup = t), (this.processChildren = n), (this.index = r);
        }
      }
      function nE(e, t, n) {
        if (
          (e || (e = new ee([], {})),
          0 === e.segments.length && e.hasChildren())
        )
          return ws(e, t, n);
        const r = (function EB(e, t, n) {
            let r = 0,
              i = t;
            const o = { match: !1, pathIndex: 0, commandIndex: 0 };
            for (; i < e.segments.length; ) {
              if (r >= n.length) return o;
              const s = e.segments[i],
                a = n[r];
              if (Ds(a)) break;
              const c = `${a}`,
                l = r < n.length - 1 ? n[r + 1] : null;
              if (i > 0 && void 0 === c) break;
              if (c && l && "object" == typeof l && void 0 === l.outlets) {
                if (!iE(c, l, s)) return o;
                r += 2;
              } else {
                if (!iE(c, {}, s)) return o;
                r++;
              }
              i++;
            }
            return { match: !0, pathIndex: i, commandIndex: r };
          })(e, t, n),
          i = n.slice(r.commandIndex);
        if (r.match && r.pathIndex < e.segments.length) {
          const o = new ee(e.segments.slice(0, r.pathIndex), {});
          return (
            (o.children[$] = new ee(e.segments.slice(r.pathIndex), e.children)),
            ws(o, 0, i)
          );
        }
        return r.match && 0 === i.length
          ? new ee(e.segments, {})
          : r.match && !e.hasChildren()
          ? Yh(e, t, n)
          : r.match
          ? ws(e, 0, i)
          : Yh(e, t, n);
      }
      function ws(e, t, n) {
        if (0 === n.length) return new ee(e.segments, {});
        {
          const r = (function wB(e) {
              return Ds(e[0]) ? e[0].outlets : { [$]: e };
            })(n),
            i = {};
          if (
            Object.keys(r).some((o) => o !== $) &&
            e.children[$] &&
            1 === e.numberOfChildren &&
            0 === e.children[$].segments.length
          ) {
            const o = ws(e.children[$], t, n);
            return new ee(e.segments, o.children);
          }
          return (
            Object.entries(r).forEach(([o, s]) => {
              "string" == typeof s && (s = [s]),
                null !== s && (i[o] = nE(e.children[o], t, s));
            }),
            Object.entries(e.children).forEach(([o, s]) => {
              void 0 === r[o] && (i[o] = s);
            }),
            new ee(e.segments, i)
          );
        }
      }
      function Yh(e, t, n) {
        const r = e.segments.slice(0, t);
        let i = 0;
        for (; i < n.length; ) {
          const o = n[i];
          if (Ds(o)) {
            const c = CB(o.outlets);
            return new ee(r, c);
          }
          if (0 === i && sl(n[0])) {
            r.push(new ys(e.segments[t].path, rE(n[0]))), i++;
            continue;
          }
          const s = Ds(o) ? o.outlets[$] : `${o}`,
            a = i < n.length - 1 ? n[i + 1] : null;
          s && a && sl(a)
            ? (r.push(new ys(s, rE(a))), (i += 2))
            : (r.push(new ys(s, {})), i++);
        }
        return new ee(r, {});
      }
      function CB(e) {
        const t = {};
        return (
          Object.entries(e).forEach(([n, r]) => {
            "string" == typeof r && (r = [r]),
              null !== r && (t[n] = Yh(new ee([], {}), 0, r));
          }),
          t
        );
      }
      function rE(e) {
        const t = {};
        return Object.entries(e).forEach(([n, r]) => (t[n] = `${r}`)), t;
      }
      function iE(e, t, n) {
        return e == n.path && dn(t, n.parameters);
      }
      const Es = "imperative";
      class fn {
        constructor(t, n) {
          (this.id = t), (this.url = n);
        }
      }
      class cl extends fn {
        constructor(t, n, r = "imperative", i = null) {
          super(t, n),
            (this.type = 0),
            (this.navigationTrigger = r),
            (this.restoredState = i);
        }
        toString() {
          return `NavigationStart(id: ${this.id}, url: '${this.url}')`;
        }
      }
      class tr extends fn {
        constructor(t, n, r) {
          super(t, n), (this.urlAfterRedirects = r), (this.type = 1);
        }
        toString() {
          return `NavigationEnd(id: ${this.id}, url: '${this.url}', urlAfterRedirects: '${this.urlAfterRedirects}')`;
        }
      }
      class Cs extends fn {
        constructor(t, n, r, i) {
          super(t, n), (this.reason = r), (this.code = i), (this.type = 2);
        }
        toString() {
          return `NavigationCancel(id: ${this.id}, url: '${this.url}')`;
        }
      }
      class zi extends fn {
        constructor(t, n, r, i) {
          super(t, n), (this.reason = r), (this.code = i), (this.type = 16);
        }
      }
      class ll extends fn {
        constructor(t, n, r, i) {
          super(t, n), (this.error = r), (this.target = i), (this.type = 3);
        }
        toString() {
          return `NavigationError(id: ${this.id}, url: '${this.url}', error: ${this.error})`;
        }
      }
      class oE extends fn {
        constructor(t, n, r, i) {
          super(t, n),
            (this.urlAfterRedirects = r),
            (this.state = i),
            (this.type = 4);
        }
        toString() {
          return `RoutesRecognized(id: ${this.id}, url: '${this.url}', urlAfterRedirects: '${this.urlAfterRedirects}', state: ${this.state})`;
        }
      }
      class IB extends fn {
        constructor(t, n, r, i) {
          super(t, n),
            (this.urlAfterRedirects = r),
            (this.state = i),
            (this.type = 7);
        }
        toString() {
          return `GuardsCheckStart(id: ${this.id}, url: '${this.url}', urlAfterRedirects: '${this.urlAfterRedirects}', state: ${this.state})`;
        }
      }
      class MB extends fn {
        constructor(t, n, r, i, o) {
          super(t, n),
            (this.urlAfterRedirects = r),
            (this.state = i),
            (this.shouldActivate = o),
            (this.type = 8);
        }
        toString() {
          return `GuardsCheckEnd(id: ${this.id}, url: '${this.url}', urlAfterRedirects: '${this.urlAfterRedirects}', state: ${this.state}, shouldActivate: ${this.shouldActivate})`;
        }
      }
      class SB extends fn {
        constructor(t, n, r, i) {
          super(t, n),
            (this.urlAfterRedirects = r),
            (this.state = i),
            (this.type = 5);
        }
        toString() {
          return `ResolveStart(id: ${this.id}, url: '${this.url}', urlAfterRedirects: '${this.urlAfterRedirects}', state: ${this.state})`;
        }
      }
      class xB extends fn {
        constructor(t, n, r, i) {
          super(t, n),
            (this.urlAfterRedirects = r),
            (this.state = i),
            (this.type = 6);
        }
        toString() {
          return `ResolveEnd(id: ${this.id}, url: '${this.url}', urlAfterRedirects: '${this.urlAfterRedirects}', state: ${this.state})`;
        }
      }
      class TB {
        constructor(t) {
          (this.route = t), (this.type = 9);
        }
        toString() {
          return `RouteConfigLoadStart(path: ${this.route.path})`;
        }
      }
      class AB {
        constructor(t) {
          (this.route = t), (this.type = 10);
        }
        toString() {
          return `RouteConfigLoadEnd(path: ${this.route.path})`;
        }
      }
      class NB {
        constructor(t) {
          (this.snapshot = t), (this.type = 11);
        }
        toString() {
          return `ChildActivationStart(path: '${
            (this.snapshot.routeConfig && this.snapshot.routeConfig.path) || ""
          }')`;
        }
      }
      class RB {
        constructor(t) {
          (this.snapshot = t), (this.type = 12);
        }
        toString() {
          return `ChildActivationEnd(path: '${
            (this.snapshot.routeConfig && this.snapshot.routeConfig.path) || ""
          }')`;
        }
      }
      class OB {
        constructor(t) {
          (this.snapshot = t), (this.type = 13);
        }
        toString() {
          return `ActivationStart(path: '${
            (this.snapshot.routeConfig && this.snapshot.routeConfig.path) || ""
          }')`;
        }
      }
      class PB {
        constructor(t) {
          (this.snapshot = t), (this.type = 14);
        }
        toString() {
          return `ActivationEnd(path: '${
            (this.snapshot.routeConfig && this.snapshot.routeConfig.path) || ""
          }')`;
        }
      }
      class sE {
        constructor(t, n, r) {
          (this.routerEvent = t),
            (this.position = n),
            (this.anchor = r),
            (this.type = 15);
        }
        toString() {
          return `Scroll(anchor: '${this.anchor}', position: '${
            this.position ? `${this.position[0]}, ${this.position[1]}` : null
          }')`;
        }
      }
      class Xh {}
      class Jh {
        constructor(t) {
          this.url = t;
        }
      }
      class kB {
        constructor() {
          (this.outlet = null),
            (this.route = null),
            (this.injector = null),
            (this.children = new Is()),
            (this.attachRef = null);
        }
      }
      let Is = (() => {
        class e {
          constructor() {
            this.contexts = new Map();
          }
          onChildOutletCreated(n, r) {
            const i = this.getOrCreateContext(n);
            (i.outlet = r), this.contexts.set(n, i);
          }
          onChildOutletDestroyed(n) {
            const r = this.getContext(n);
            r && ((r.outlet = null), (r.attachRef = null));
          }
          onOutletDeactivated() {
            const n = this.contexts;
            return (this.contexts = new Map()), n;
          }
          onOutletReAttached(n) {
            this.contexts = n;
          }
          getOrCreateContext(n) {
            let r = this.getContext(n);
            return r || ((r = new kB()), this.contexts.set(n, r)), r;
          }
          getContext(n) {
            return this.contexts.get(n) || null;
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      class aE {
        constructor(t) {
          this._root = t;
        }
        get root() {
          return this._root.value;
        }
        parent(t) {
          const n = this.pathFromRoot(t);
          return n.length > 1 ? n[n.length - 2] : null;
        }
        children(t) {
          const n = ep(t, this._root);
          return n ? n.children.map((r) => r.value) : [];
        }
        firstChild(t) {
          const n = ep(t, this._root);
          return n && n.children.length > 0 ? n.children[0].value : null;
        }
        siblings(t) {
          const n = tp(t, this._root);
          return n.length < 2
            ? []
            : n[n.length - 2].children
                .map((i) => i.value)
                .filter((i) => i !== t);
        }
        pathFromRoot(t) {
          return tp(t, this._root).map((n) => n.value);
        }
      }
      function ep(e, t) {
        if (e === t.value) return t;
        for (const n of t.children) {
          const r = ep(e, n);
          if (r) return r;
        }
        return null;
      }
      function tp(e, t) {
        if (e === t.value) return [t];
        for (const n of t.children) {
          const r = tp(e, n);
          if (r.length) return r.unshift(t), r;
        }
        return [];
      }
      class Rn {
        constructor(t, n) {
          (this.value = t), (this.children = n);
        }
        toString() {
          return `TreeNode(${this.value})`;
        }
      }
      function qi(e) {
        const t = {};
        return e && e.children.forEach((n) => (t[n.value.outlet] = n)), t;
      }
      class cE extends aE {
        constructor(t, n) {
          super(t), (this.snapshot = n), np(this, t);
        }
        toString() {
          return this.snapshot.toString();
        }
      }
      function lE(e, t) {
        const n = (function FB(e, t) {
            const s = new ul([], {}, {}, "", {}, $, t, null, {});
            return new dE("", new Rn(s, []));
          })(0, t),
          r = new lt([new ys("", {})]),
          i = new lt({}),
          o = new lt({}),
          s = new lt({}),
          a = new lt(""),
          c = new Gi(r, i, s, a, o, $, t, n.root);
        return (c.snapshot = n.root), new cE(new Rn(c, []), n);
      }
      class Gi {
        constructor(t, n, r, i, o, s, a, c) {
          (this.urlSubject = t),
            (this.paramsSubject = n),
            (this.queryParamsSubject = r),
            (this.fragmentSubject = i),
            (this.dataSubject = o),
            (this.outlet = s),
            (this.component = a),
            (this._futureSnapshot = c),
            (this.title = this.dataSubject?.pipe(U((l) => l[bs])) ?? A(void 0)),
            (this.url = t),
            (this.params = n),
            (this.queryParams = r),
            (this.fragment = i),
            (this.data = o);
        }
        get routeConfig() {
          return this._futureSnapshot.routeConfig;
        }
        get root() {
          return this._routerState.root;
        }
        get parent() {
          return this._routerState.parent(this);
        }
        get firstChild() {
          return this._routerState.firstChild(this);
        }
        get children() {
          return this._routerState.children(this);
        }
        get pathFromRoot() {
          return this._routerState.pathFromRoot(this);
        }
        get paramMap() {
          return (
            this._paramMap ||
              (this._paramMap = this.params.pipe(U((t) => Ui(t)))),
            this._paramMap
          );
        }
        get queryParamMap() {
          return (
            this._queryParamMap ||
              (this._queryParamMap = this.queryParams.pipe(U((t) => Ui(t)))),
            this._queryParamMap
          );
        }
        toString() {
          return this.snapshot
            ? this.snapshot.toString()
            : `Future(${this._futureSnapshot})`;
        }
      }
      function uE(e, t = "emptyOnly") {
        const n = e.pathFromRoot;
        let r = 0;
        if ("always" !== t)
          for (r = n.length - 1; r >= 1; ) {
            const i = n[r],
              o = n[r - 1];
            if (i.routeConfig && "" === i.routeConfig.path) r--;
            else {
              if (o.component) break;
              r--;
            }
          }
        return (function LB(e) {
          return e.reduce(
            (t, n) => ({
              params: { ...t.params, ...n.params },
              data: { ...t.data, ...n.data },
              resolve: {
                ...n.data,
                ...t.resolve,
                ...n.routeConfig?.data,
                ...n._resolvedData,
              },
            }),
            { params: {}, data: {}, resolve: {} },
          );
        })(n.slice(r));
      }
      class ul {
        get title() {
          return this.data?.[bs];
        }
        constructor(t, n, r, i, o, s, a, c, l) {
          (this.url = t),
            (this.params = n),
            (this.queryParams = r),
            (this.fragment = i),
            (this.data = o),
            (this.outlet = s),
            (this.component = a),
            (this.routeConfig = c),
            (this._resolve = l);
        }
        get root() {
          return this._routerState.root;
        }
        get parent() {
          return this._routerState.parent(this);
        }
        get firstChild() {
          return this._routerState.firstChild(this);
        }
        get children() {
          return this._routerState.children(this);
        }
        get pathFromRoot() {
          return this._routerState.pathFromRoot(this);
        }
        get paramMap() {
          return (
            this._paramMap || (this._paramMap = Ui(this.params)), this._paramMap
          );
        }
        get queryParamMap() {
          return (
            this._queryParamMap || (this._queryParamMap = Ui(this.queryParams)),
            this._queryParamMap
          );
        }
        toString() {
          return `Route(url:'${this.url
            .map((r) => r.toString())
            .join("/")}', path:'${
            this.routeConfig ? this.routeConfig.path : ""
          }')`;
        }
      }
      class dE extends aE {
        constructor(t, n) {
          super(n), (this.url = t), np(this, n);
        }
        toString() {
          return fE(this._root);
        }
      }
      function np(e, t) {
        (t.value._routerState = e), t.children.forEach((n) => np(e, n));
      }
      function fE(e) {
        const t =
          e.children.length > 0 ? ` { ${e.children.map(fE).join(", ")} } ` : "";
        return `${e.value}${t}`;
      }
      function rp(e) {
        if (e.snapshot) {
          const t = e.snapshot,
            n = e._futureSnapshot;
          (e.snapshot = n),
            dn(t.queryParams, n.queryParams) ||
              e.queryParamsSubject.next(n.queryParams),
            t.fragment !== n.fragment && e.fragmentSubject.next(n.fragment),
            dn(t.params, n.params) || e.paramsSubject.next(n.params),
            (function Jj(e, t) {
              if (e.length !== t.length) return !1;
              for (let n = 0; n < e.length; ++n) if (!dn(e[n], t[n])) return !1;
              return !0;
            })(t.url, n.url) || e.urlSubject.next(n.url),
            dn(t.data, n.data) || e.dataSubject.next(n.data);
        } else
          (e.snapshot = e._futureSnapshot),
            e.dataSubject.next(e._futureSnapshot.data);
      }
      function ip(e, t) {
        const n =
          dn(e.params, t.params) &&
          (function rB(e, t) {
            return (
              xr(e, t) && e.every((n, r) => dn(n.parameters, t[r].parameters))
            );
          })(e.url, t.url);
        return (
          n &&
          !(!e.parent != !t.parent) &&
          (!e.parent || ip(e.parent, t.parent))
        );
      }
      let op = (() => {
        class e {
          constructor() {
            (this.activated = null),
              (this._activatedRoute = null),
              (this.name = $),
              (this.activateEvents = new Ye()),
              (this.deactivateEvents = new Ye()),
              (this.attachEvents = new Ye()),
              (this.detachEvents = new Ye()),
              (this.parentContexts = C(Is)),
              (this.location = C(Ut)),
              (this.changeDetector = C(Rf)),
              (this.environmentInjector = C(mt)),
              (this.inputBinder = C(dl, { optional: !0 })),
              (this.supportsBindingToComponentInputs = !0);
          }
          get activatedComponentRef() {
            return this.activated;
          }
          ngOnChanges(n) {
            if (n.name) {
              const { firstChange: r, previousValue: i } = n.name;
              if (r) return;
              this.isTrackedInParentContexts(i) &&
                (this.deactivate(),
                this.parentContexts.onChildOutletDestroyed(i)),
                this.initializeOutletWithName();
            }
          }
          ngOnDestroy() {
            this.isTrackedInParentContexts(this.name) &&
              this.parentContexts.onChildOutletDestroyed(this.name),
              this.inputBinder?.unsubscribeFromRouteData(this);
          }
          isTrackedInParentContexts(n) {
            return this.parentContexts.getContext(n)?.outlet === this;
          }
          ngOnInit() {
            this.initializeOutletWithName();
          }
          initializeOutletWithName() {
            if (
              (this.parentContexts.onChildOutletCreated(this.name, this),
              this.activated)
            )
              return;
            const n = this.parentContexts.getContext(this.name);
            n?.route &&
              (n.attachRef
                ? this.attach(n.attachRef, n.route)
                : this.activateWith(n.route, n.injector));
          }
          get isActivated() {
            return !!this.activated;
          }
          get component() {
            if (!this.activated) throw new v(4012, !1);
            return this.activated.instance;
          }
          get activatedRoute() {
            if (!this.activated) throw new v(4012, !1);
            return this._activatedRoute;
          }
          get activatedRouteData() {
            return this._activatedRoute
              ? this._activatedRoute.snapshot.data
              : {};
          }
          detach() {
            if (!this.activated) throw new v(4012, !1);
            this.location.detach();
            const n = this.activated;
            return (
              (this.activated = null),
              (this._activatedRoute = null),
              this.detachEvents.emit(n.instance),
              n
            );
          }
          attach(n, r) {
            (this.activated = n),
              (this._activatedRoute = r),
              this.location.insert(n.hostView),
              this.inputBinder?.bindActivatedRouteToOutletComponent(this),
              this.attachEvents.emit(n.instance);
          }
          deactivate() {
            if (this.activated) {
              const n = this.component;
              this.activated.destroy(),
                (this.activated = null),
                (this._activatedRoute = null),
                this.deactivateEvents.emit(n);
            }
          }
          activateWith(n, r) {
            if (this.isActivated) throw new v(4013, !1);
            this._activatedRoute = n;
            const i = this.location,
              s = n.snapshot.component,
              a = this.parentContexts.getOrCreateContext(this.name).children,
              c = new jB(n, a, i.injector);
            (this.activated = i.createComponent(s, {
              index: i.length,
              injector: c,
              environmentInjector: r ?? this.environmentInjector,
            })),
              this.changeDetector.markForCheck(),
              this.inputBinder?.bindActivatedRouteToOutletComponent(this),
              this.activateEvents.emit(this.activated.instance);
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵdir = re({
              type: e,
              selectors: [["router-outlet"]],
              inputs: { name: "name" },
              outputs: {
                activateEvents: "activate",
                deactivateEvents: "deactivate",
                attachEvents: "attach",
                detachEvents: "detach",
              },
              exportAs: ["outlet"],
              standalone: !0,
              features: [cr],
            });
          }
        }
        return e;
      })();
      class jB {
        constructor(t, n, r) {
          (this.route = t), (this.childContexts = n), (this.parent = r);
        }
        get(t, n) {
          return t === Gi
            ? this.route
            : t === Is
            ? this.childContexts
            : this.parent.get(t, n);
        }
      }
      const dl = new E("");
      let hE = (() => {
        class e {
          constructor() {
            this.outletDataSubscriptions = new Map();
          }
          bindActivatedRouteToOutletComponent(n) {
            this.unsubscribeFromRouteData(n), this.subscribeToRouteData(n);
          }
          unsubscribeFromRouteData(n) {
            this.outletDataSubscriptions.get(n)?.unsubscribe(),
              this.outletDataSubscriptions.delete(n);
          }
          subscribeToRouteData(n) {
            const { activatedRoute: r } = n,
              i = Xc([r.queryParams, r.params, r.data])
                .pipe(
                  Ft(
                    ([o, s, a], c) => (
                      (a = { ...o, ...s, ...a }),
                      0 === c ? A(a) : Promise.resolve(a)
                    ),
                  ),
                )
                .subscribe((o) => {
                  if (
                    !n.isActivated ||
                    !n.activatedComponentRef ||
                    n.activatedRoute !== r ||
                    null === r.component
                  )
                    return void this.unsubscribeFromRouteData(n);
                  const s = (function UP(e) {
                    const t = q(e);
                    if (!t) return null;
                    const n = new $o(t);
                    return {
                      get selector() {
                        return n.selector;
                      },
                      get type() {
                        return n.componentType;
                      },
                      get inputs() {
                        return n.inputs;
                      },
                      get outputs() {
                        return n.outputs;
                      },
                      get ngContentSelectors() {
                        return n.ngContentSelectors;
                      },
                      get isStandalone() {
                        return t.standalone;
                      },
                      get isSignal() {
                        return t.signals;
                      },
                    };
                  })(r.component);
                  if (s)
                    for (const { templateName: a } of s.inputs)
                      n.activatedComponentRef.setInput(a, o[a]);
                  else this.unsubscribeFromRouteData(n);
                });
            this.outletDataSubscriptions.set(n, i);
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      function Ms(e, t, n) {
        if (n && e.shouldReuseRoute(t.value, n.value.snapshot)) {
          const r = n.value;
          r._futureSnapshot = t.value;
          const i = (function VB(e, t, n) {
            return t.children.map((r) => {
              for (const i of n.children)
                if (e.shouldReuseRoute(r.value, i.value.snapshot))
                  return Ms(e, r, i);
              return Ms(e, r);
            });
          })(e, t, n);
          return new Rn(r, i);
        }
        {
          if (e.shouldAttach(t.value)) {
            const o = e.retrieve(t.value);
            if (null !== o) {
              const s = o.route;
              return (
                (s.value._futureSnapshot = t.value),
                (s.children = t.children.map((a) => Ms(e, a))),
                s
              );
            }
          }
          const r = (function $B(e) {
              return new Gi(
                new lt(e.url),
                new lt(e.params),
                new lt(e.queryParams),
                new lt(e.fragment),
                new lt(e.data),
                e.outlet,
                e.component,
                e,
              );
            })(t.value),
            i = t.children.map((o) => Ms(e, o));
          return new Rn(r, i);
        }
      }
      const sp = "ngNavigationCancelingError";
      function pE(e, t) {
        const { redirectTo: n, navigationBehaviorOptions: r } = Tr(t)
            ? { redirectTo: t, navigationBehaviorOptions: void 0 }
            : t,
          i = mE(!1, 0, t);
        return (i.url = n), (i.navigationBehaviorOptions = r), i;
      }
      function mE(e, t, n) {
        const r = new Error("NavigationCancelingError: " + (e || ""));
        return (r[sp] = !0), (r.cancellationCode = t), n && (r.url = n), r;
      }
      function gE(e) {
        return e && e[sp];
      }
      let bE = (() => {
        class e {
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵcmp = bn({
              type: e,
              selectors: [["ng-component"]],
              standalone: !0,
              features: [f_],
              decls: 1,
              vars: 0,
              template: function (r, i) {
                1 & r && gr(0, "router-outlet");
              },
              dependencies: [op],
              encapsulation: 2,
            });
          }
        }
        return e;
      })();
      function ap(e) {
        const t = e.children && e.children.map(ap),
          n = t ? { ...e, children: t } : { ...e };
        return (
          !n.component &&
            !n.loadComponent &&
            (t || n.loadChildren) &&
            n.outlet &&
            n.outlet !== $ &&
            (n.component = bE),
          n
        );
      }
      function Wt(e) {
        return e.outlet || $;
      }
      function Ss(e) {
        if (!e) return null;
        if (e.routeConfig?._injector) return e.routeConfig._injector;
        for (let t = e.parent; t; t = t.parent) {
          const n = t.routeConfig;
          if (n?._loadedInjector) return n._loadedInjector;
          if (n?._injector) return n._injector;
        }
        return null;
      }
      class ZB {
        constructor(t, n, r, i, o) {
          (this.routeReuseStrategy = t),
            (this.futureState = n),
            (this.currState = r),
            (this.forwardEvent = i),
            (this.inputBindingEnabled = o);
        }
        activate(t) {
          const n = this.futureState._root,
            r = this.currState ? this.currState._root : null;
          this.deactivateChildRoutes(n, r, t),
            rp(this.futureState.root),
            this.activateChildRoutes(n, r, t);
        }
        deactivateChildRoutes(t, n, r) {
          const i = qi(n);
          t.children.forEach((o) => {
            const s = o.value.outlet;
            this.deactivateRoutes(o, i[s], r), delete i[s];
          }),
            Object.values(i).forEach((o) => {
              this.deactivateRouteAndItsChildren(o, r);
            });
        }
        deactivateRoutes(t, n, r) {
          const i = t.value,
            o = n ? n.value : null;
          if (i === o)
            if (i.component) {
              const s = r.getContext(i.outlet);
              s && this.deactivateChildRoutes(t, n, s.children);
            } else this.deactivateChildRoutes(t, n, r);
          else o && this.deactivateRouteAndItsChildren(n, r);
        }
        deactivateRouteAndItsChildren(t, n) {
          t.value.component &&
          this.routeReuseStrategy.shouldDetach(t.value.snapshot)
            ? this.detachAndStoreRouteSubtree(t, n)
            : this.deactivateRouteAndOutlet(t, n);
        }
        detachAndStoreRouteSubtree(t, n) {
          const r = n.getContext(t.value.outlet),
            i = r && t.value.component ? r.children : n,
            o = qi(t);
          for (const s of Object.keys(o))
            this.deactivateRouteAndItsChildren(o[s], i);
          if (r && r.outlet) {
            const s = r.outlet.detach(),
              a = r.children.onOutletDeactivated();
            this.routeReuseStrategy.store(t.value.snapshot, {
              componentRef: s,
              route: t,
              contexts: a,
            });
          }
        }
        deactivateRouteAndOutlet(t, n) {
          const r = n.getContext(t.value.outlet),
            i = r && t.value.component ? r.children : n,
            o = qi(t);
          for (const s of Object.keys(o))
            this.deactivateRouteAndItsChildren(o[s], i);
          r &&
            (r.outlet &&
              (r.outlet.deactivate(), r.children.onOutletDeactivated()),
            (r.attachRef = null),
            (r.route = null));
        }
        activateChildRoutes(t, n, r) {
          const i = qi(n);
          t.children.forEach((o) => {
            this.activateRoutes(o, i[o.value.outlet], r),
              this.forwardEvent(new PB(o.value.snapshot));
          }),
            t.children.length && this.forwardEvent(new RB(t.value.snapshot));
        }
        activateRoutes(t, n, r) {
          const i = t.value,
            o = n ? n.value : null;
          if ((rp(i), i === o))
            if (i.component) {
              const s = r.getOrCreateContext(i.outlet);
              this.activateChildRoutes(t, n, s.children);
            } else this.activateChildRoutes(t, n, r);
          else if (i.component) {
            const s = r.getOrCreateContext(i.outlet);
            if (this.routeReuseStrategy.shouldAttach(i.snapshot)) {
              const a = this.routeReuseStrategy.retrieve(i.snapshot);
              this.routeReuseStrategy.store(i.snapshot, null),
                s.children.onOutletReAttached(a.contexts),
                (s.attachRef = a.componentRef),
                (s.route = a.route.value),
                s.outlet && s.outlet.attach(a.componentRef, a.route.value),
                rp(a.route.value),
                this.activateChildRoutes(t, null, s.children);
            } else {
              const a = Ss(i.snapshot);
              (s.attachRef = null),
                (s.route = i),
                (s.injector = a),
                s.outlet && s.outlet.activateWith(i, s.injector),
                this.activateChildRoutes(t, null, s.children);
            }
          } else this.activateChildRoutes(t, null, r);
        }
      }
      class yE {
        constructor(t) {
          (this.path = t), (this.route = this.path[this.path.length - 1]);
        }
      }
      class fl {
        constructor(t, n) {
          (this.component = t), (this.route = n);
        }
      }
      function QB(e, t, n) {
        const r = e._root;
        return xs(r, t ? t._root : null, n, [r.value]);
      }
      function Wi(e, t) {
        const n = Symbol(),
          r = t.get(e, n);
        return r === n
          ? "function" != typeof e ||
            (function BI(e) {
              return null !== qs(e);
            })(e)
            ? t.get(e)
            : e
          : r;
      }
      function xs(
        e,
        t,
        n,
        r,
        i = { canDeactivateChecks: [], canActivateChecks: [] },
      ) {
        const o = qi(t);
        return (
          e.children.forEach((s) => {
            (function XB(
              e,
              t,
              n,
              r,
              i = { canDeactivateChecks: [], canActivateChecks: [] },
            ) {
              const o = e.value,
                s = t ? t.value : null,
                a = n ? n.getContext(e.value.outlet) : null;
              if (s && o.routeConfig === s.routeConfig) {
                const c = (function JB(e, t, n) {
                  if ("function" == typeof n) return n(e, t);
                  switch (n) {
                    case "pathParamsChange":
                      return !xr(e.url, t.url);
                    case "pathParamsOrQueryParamsChange":
                      return (
                        !xr(e.url, t.url) || !dn(e.queryParams, t.queryParams)
                      );
                    case "always":
                      return !0;
                    case "paramsOrQueryParamsChange":
                      return !ip(e, t) || !dn(e.queryParams, t.queryParams);
                    default:
                      return !ip(e, t);
                  }
                })(s, o, o.routeConfig.runGuardsAndResolvers);
                c
                  ? i.canActivateChecks.push(new yE(r))
                  : ((o.data = s.data), (o._resolvedData = s._resolvedData)),
                  xs(e, t, o.component ? (a ? a.children : null) : n, r, i),
                  c &&
                    a &&
                    a.outlet &&
                    a.outlet.isActivated &&
                    i.canDeactivateChecks.push(new fl(a.outlet.component, s));
              } else
                s && Ts(t, a, i),
                  i.canActivateChecks.push(new yE(r)),
                  xs(e, null, o.component ? (a ? a.children : null) : n, r, i);
            })(s, o[s.value.outlet], n, r.concat([s.value]), i),
              delete o[s.value.outlet];
          }),
          Object.entries(o).forEach(([s, a]) => Ts(a, n.getContext(s), i)),
          i
        );
      }
      function Ts(e, t, n) {
        const r = qi(e),
          i = e.value;
        Object.entries(r).forEach(([o, s]) => {
          Ts(s, i.component ? (t ? t.children.getContext(o) : null) : t, n);
        }),
          n.canDeactivateChecks.push(
            new fl(
              i.component && t && t.outlet && t.outlet.isActivated
                ? t.outlet.component
                : null,
              i,
            ),
          );
      }
      function As(e) {
        return "function" == typeof e;
      }
      function vE(e) {
        return e instanceof Jc || "EmptyError" === e?.name;
      }
      const hl = Symbol("INITIAL_VALUE");
      function Ki() {
        return Ft((e) =>
          Xc(e.map((t) => t.pipe(Nn(1), jw(hl)))).pipe(
            U((t) => {
              for (const n of t)
                if (!0 !== n) {
                  if (n === hl) return hl;
                  if (!1 === n || n instanceof Hi) return n;
                }
              return !0;
            }),
            Gt((t) => t !== hl),
            Nn(1),
          ),
        );
      }
      function _E(e) {
        return (function LC(...e) {
          return Ip(e);
        })(
          Ee((t) => {
            if (Tr(t)) throw pE(0, t);
          }),
          U((t) => !0 === t),
        );
      }
      class pl {
        constructor(t) {
          this.segmentGroup = t || null;
        }
      }
      class DE {
        constructor(t) {
          this.urlTree = t;
        }
      }
      function Zi(e) {
        return $i(new pl(e));
      }
      function wE(e) {
        return $i(new DE(e));
      }
      class vV {
        constructor(t, n) {
          (this.urlSerializer = t), (this.urlTree = n);
        }
        noMatchError(t) {
          return new v(4002, !1);
        }
        lineralizeSegments(t, n) {
          let r = [],
            i = n.root;
          for (;;) {
            if (((r = r.concat(i.segments)), 0 === i.numberOfChildren))
              return A(r);
            if (i.numberOfChildren > 1 || !i.children[$])
              return $i(new v(4e3, !1));
            i = i.children[$];
          }
        }
        applyRedirectCommands(t, n, r) {
          return this.applyRedirectCreateUrlTree(
            n,
            this.urlSerializer.parse(n),
            t,
            r,
          );
        }
        applyRedirectCreateUrlTree(t, n, r, i) {
          const o = this.createSegmentGroup(t, n.root, r, i);
          return new Hi(
            o,
            this.createQueryParams(n.queryParams, this.urlTree.queryParams),
            n.fragment,
          );
        }
        createQueryParams(t, n) {
          const r = {};
          return (
            Object.entries(t).forEach(([i, o]) => {
              if ("string" == typeof o && o.startsWith(":")) {
                const a = o.substring(1);
                r[i] = n[a];
              } else r[i] = o;
            }),
            r
          );
        }
        createSegmentGroup(t, n, r, i) {
          const o = this.createSegments(t, n.segments, r, i);
          let s = {};
          return (
            Object.entries(n.children).forEach(([a, c]) => {
              s[a] = this.createSegmentGroup(t, c, r, i);
            }),
            new ee(o, s)
          );
        }
        createSegments(t, n, r, i) {
          return n.map((o) =>
            o.path.startsWith(":")
              ? this.findPosParam(t, o, i)
              : this.findOrReturn(o, r),
          );
        }
        findPosParam(t, n, r) {
          const i = r[n.path.substring(1)];
          if (!i) throw new v(4001, !1);
          return i;
        }
        findOrReturn(t, n) {
          let r = 0;
          for (const i of n) {
            if (i.path === t.path) return n.splice(r), i;
            r++;
          }
          return t;
        }
      }
      const cp = {
        matched: !1,
        consumedSegments: [],
        remainingSegments: [],
        parameters: {},
        positionalParamSegments: {},
      };
      function _V(e, t, n, r, i) {
        const o = lp(e, t, n);
        return o.matched
          ? ((r = (function HB(e, t) {
              return (
                e.providers &&
                  !e._injector &&
                  (e._injector = lf(e.providers, t, `Route: ${e.path}`)),
                e._injector ?? t
              );
            })(t, r)),
            (function gV(e, t, n, r) {
              const i = t.canMatch;
              return i && 0 !== i.length
                ? A(
                    i.map((s) => {
                      const a = Wi(s, e);
                      return er(
                        (function oV(e) {
                          return e && As(e.canMatch);
                        })(a)
                          ? a.canMatch(t, n)
                          : e.runInContext(() => a(t, n)),
                      );
                    }),
                  ).pipe(Ki(), _E())
                : A(!0);
            })(r, t, n).pipe(U((s) => (!0 === s ? o : { ...cp }))))
          : A(o);
      }
      function lp(e, t, n) {
        if ("" === t.path)
          return "full" === t.pathMatch && (e.hasChildren() || n.length > 0)
            ? { ...cp }
            : {
                matched: !0,
                consumedSegments: [],
                remainingSegments: n,
                parameters: {},
                positionalParamSegments: {},
              };
        const i = (t.matcher || Xj)(n, e, t);
        if (!i) return { ...cp };
        const o = {};
        Object.entries(i.posParams ?? {}).forEach(([a, c]) => {
          o[a] = c.path;
        });
        const s =
          i.consumed.length > 0
            ? { ...o, ...i.consumed[i.consumed.length - 1].parameters }
            : o;
        return {
          matched: !0,
          consumedSegments: i.consumed,
          remainingSegments: n.slice(i.consumed.length),
          parameters: s,
          positionalParamSegments: i.posParams ?? {},
        };
      }
      function EE(e, t, n, r) {
        return n.length > 0 &&
          (function EV(e, t, n) {
            return n.some((r) => ml(e, t, r) && Wt(r) !== $);
          })(e, n, r)
          ? {
              segmentGroup: new ee(t, wV(r, new ee(n, e.children))),
              slicedSegments: [],
            }
          : 0 === n.length &&
            (function CV(e, t, n) {
              return n.some((r) => ml(e, t, r));
            })(e, n, r)
          ? {
              segmentGroup: new ee(e.segments, DV(e, 0, n, r, e.children)),
              slicedSegments: n,
            }
          : { segmentGroup: new ee(e.segments, e.children), slicedSegments: n };
      }
      function DV(e, t, n, r, i) {
        const o = {};
        for (const s of r)
          if (ml(e, n, s) && !i[Wt(s)]) {
            const a = new ee([], {});
            o[Wt(s)] = a;
          }
        return { ...i, ...o };
      }
      function wV(e, t) {
        const n = {};
        n[$] = t;
        for (const r of e)
          if ("" === r.path && Wt(r) !== $) {
            const i = new ee([], {});
            n[Wt(r)] = i;
          }
        return n;
      }
      function ml(e, t, n) {
        return (
          (!(e.hasChildren() || t.length > 0) || "full" !== n.pathMatch) &&
          "" === n.path
        );
      }
      class xV {
        constructor(t, n, r, i, o, s, a) {
          (this.injector = t),
            (this.configLoader = n),
            (this.rootComponentType = r),
            (this.config = i),
            (this.urlTree = o),
            (this.paramsInheritanceStrategy = s),
            (this.urlSerializer = a),
            (this.allowRedirects = !0),
            (this.applyRedirects = new vV(this.urlSerializer, this.urlTree));
        }
        noMatchError(t) {
          return new v(4002, !1);
        }
        recognize() {
          const t = EE(this.urlTree.root, [], [], this.config).segmentGroup;
          return this.processSegmentGroup(
            this.injector,
            this.config,
            t,
            $,
          ).pipe(
            Jn((n) => {
              if (n instanceof DE)
                return (
                  (this.allowRedirects = !1),
                  (this.urlTree = n.urlTree),
                  this.match(n.urlTree)
                );
              throw n instanceof pl ? this.noMatchError(n) : n;
            }),
            U((n) => {
              const r = new ul(
                  [],
                  Object.freeze({}),
                  Object.freeze({ ...this.urlTree.queryParams }),
                  this.urlTree.fragment,
                  {},
                  $,
                  this.rootComponentType,
                  null,
                  {},
                ),
                i = new Rn(r, n),
                o = new dE("", i),
                s = (function yB(e, t, n = null, r = null) {
                  return Jw(Xw(e), t, n, r);
                })(r, [], this.urlTree.queryParams, this.urlTree.fragment);
              return (
                (s.queryParams = this.urlTree.queryParams),
                (o.url = this.urlSerializer.serialize(s)),
                this.inheritParamsAndData(o._root),
                { state: o, tree: s }
              );
            }),
          );
        }
        match(t) {
          return this.processSegmentGroup(
            this.injector,
            this.config,
            t.root,
            $,
          ).pipe(
            Jn((r) => {
              throw r instanceof pl ? this.noMatchError(r) : r;
            }),
          );
        }
        inheritParamsAndData(t) {
          const n = t.value,
            r = uE(n, this.paramsInheritanceStrategy);
          (n.params = Object.freeze(r.params)),
            (n.data = Object.freeze(r.data)),
            t.children.forEach((i) => this.inheritParamsAndData(i));
        }
        processSegmentGroup(t, n, r, i) {
          return 0 === r.segments.length && r.hasChildren()
            ? this.processChildren(t, n, r)
            : this.processSegment(t, n, r, r.segments, i, !0);
        }
        processChildren(t, n, r) {
          const i = [];
          for (const o of Object.keys(r.children))
            "primary" === o ? i.unshift(o) : i.push(o);
          return Se(i).pipe(
            Li((o) => {
              const s = r.children[o],
                a = (function WB(e, t) {
                  const n = e.filter((r) => Wt(r) === t);
                  return n.push(...e.filter((r) => Wt(r) !== t)), n;
                })(n, o);
              return this.processSegmentGroup(t, a, s, o);
            }),
            (function Kj(e, t) {
              return De(
                (function Wj(e, t, n, r, i) {
                  return (o, s) => {
                    let a = n,
                      c = t,
                      l = 0;
                    o.subscribe(
                      be(
                        s,
                        (u) => {
                          const d = l++;
                          (c = a ? e(c, u, d) : ((a = !0), u)), r && s.next(c);
                        },
                        i &&
                          (() => {
                            a && s.next(c), s.complete();
                          }),
                      ),
                    );
                  };
                })(e, t, arguments.length >= 2, !0),
              );
            })((o, s) => (o.push(...s), o)),
            tl(null),
            (function Zj(e, t) {
              const n = arguments.length >= 2;
              return (r) =>
                r.pipe(
                  e ? Gt((i, o) => e(i, o, r)) : kn,
                  qh(1),
                  n ? tl(t) : Bw(() => new Jc()),
                );
            })(),
            Ae((o) => {
              if (null === o) return Zi(r);
              const s = CE(o);
              return (
                (function TV(e) {
                  e.sort((t, n) =>
                    t.value.outlet === $
                      ? -1
                      : n.value.outlet === $
                      ? 1
                      : t.value.outlet.localeCompare(n.value.outlet),
                  );
                })(s),
                A(s)
              );
            }),
          );
        }
        processSegment(t, n, r, i, o, s) {
          return Se(n).pipe(
            Li((a) =>
              this.processSegmentAgainstRoute(
                a._injector ?? t,
                n,
                a,
                r,
                i,
                o,
                s,
              ).pipe(
                Jn((c) => {
                  if (c instanceof pl) return A(null);
                  throw c;
                }),
              ),
            ),
            Sr((a) => !!a),
            Jn((a) => {
              if (vE(a))
                return (function MV(e, t, n) {
                  return 0 === t.length && !e.children[n];
                })(r, i, o)
                  ? A([])
                  : Zi(r);
              throw a;
            }),
          );
        }
        processSegmentAgainstRoute(t, n, r, i, o, s, a) {
          return (function IV(e, t, n, r) {
            return (
              !!(Wt(e) === r || (r !== $ && ml(t, n, e))) &&
              ("**" === e.path || lp(t, e, n).matched)
            );
          })(r, i, o, s)
            ? void 0 === r.redirectTo
              ? this.matchSegmentAgainstRoute(t, i, r, o, s, a)
              : a && this.allowRedirects
              ? this.expandSegmentAgainstRouteUsingRedirect(t, i, n, r, o, s)
              : Zi(i)
            : Zi(i);
        }
        expandSegmentAgainstRouteUsingRedirect(t, n, r, i, o, s) {
          return "**" === i.path
            ? this.expandWildCardWithParamsAgainstRouteUsingRedirect(t, r, i, s)
            : this.expandRegularSegmentAgainstRouteUsingRedirect(
                t,
                n,
                r,
                i,
                o,
                s,
              );
        }
        expandWildCardWithParamsAgainstRouteUsingRedirect(t, n, r, i) {
          const o = this.applyRedirects.applyRedirectCommands(
            [],
            r.redirectTo,
            {},
          );
          return r.redirectTo.startsWith("/")
            ? wE(o)
            : this.applyRedirects.lineralizeSegments(r, o).pipe(
                Ae((s) => {
                  const a = new ee(s, {});
                  return this.processSegment(t, n, a, s, i, !1);
                }),
              );
        }
        expandRegularSegmentAgainstRouteUsingRedirect(t, n, r, i, o, s) {
          const {
            matched: a,
            consumedSegments: c,
            remainingSegments: l,
            positionalParamSegments: u,
          } = lp(n, i, o);
          if (!a) return Zi(n);
          const d = this.applyRedirects.applyRedirectCommands(
            c,
            i.redirectTo,
            u,
          );
          return i.redirectTo.startsWith("/")
            ? wE(d)
            : this.applyRedirects
                .lineralizeSegments(i, d)
                .pipe(
                  Ae((f) => this.processSegment(t, r, n, f.concat(l), s, !1)),
                );
        }
        matchSegmentAgainstRoute(t, n, r, i, o, s) {
          let a;
          if ("**" === r.path) {
            const c = i.length > 0 ? $w(i).parameters : {};
            (a = A({
              snapshot: new ul(
                i,
                c,
                Object.freeze({ ...this.urlTree.queryParams }),
                this.urlTree.fragment,
                IE(r),
                Wt(r),
                r.component ?? r._loadedComponent ?? null,
                r,
                ME(r),
              ),
              consumedSegments: [],
              remainingSegments: [],
            })),
              (n.children = {});
          } else
            a = _V(n, r, i, t).pipe(
              U(
                ({
                  matched: c,
                  consumedSegments: l,
                  remainingSegments: u,
                  parameters: d,
                }) =>
                  c
                    ? {
                        snapshot: new ul(
                          l,
                          d,
                          Object.freeze({ ...this.urlTree.queryParams }),
                          this.urlTree.fragment,
                          IE(r),
                          Wt(r),
                          r.component ?? r._loadedComponent ?? null,
                          r,
                          ME(r),
                        ),
                        consumedSegments: l,
                        remainingSegments: u,
                      }
                    : null,
              ),
            );
          return a.pipe(
            Ft((c) =>
              null === c
                ? Zi(n)
                : this.getChildConfig((t = r._injector ?? t), r, i).pipe(
                    Ft(({ routes: l }) => {
                      const u = r._loadedInjector ?? t,
                        {
                          snapshot: d,
                          consumedSegments: f,
                          remainingSegments: h,
                        } = c,
                        { segmentGroup: p, slicedSegments: m } = EE(n, f, h, l);
                      if (0 === m.length && p.hasChildren())
                        return this.processChildren(u, l, p).pipe(
                          U((y) => (null === y ? null : [new Rn(d, y)])),
                        );
                      if (0 === l.length && 0 === m.length)
                        return A([new Rn(d, [])]);
                      const g = Wt(r) === o;
                      return this.processSegment(
                        u,
                        l,
                        p,
                        m,
                        g ? $ : o,
                        !0,
                      ).pipe(U((y) => [new Rn(d, y)]));
                    }),
                  ),
            ),
          );
        }
        getChildConfig(t, n, r) {
          return n.children
            ? A({ routes: n.children, injector: t })
            : n.loadChildren
            ? void 0 !== n._loadedRoutes
              ? A({ routes: n._loadedRoutes, injector: n._loadedInjector })
              : (function mV(e, t, n, r) {
                  const i = t.canLoad;
                  return void 0 === i || 0 === i.length
                    ? A(!0)
                    : A(
                        i.map((s) => {
                          const a = Wi(s, e);
                          return er(
                            (function tV(e) {
                              return e && As(e.canLoad);
                            })(a)
                              ? a.canLoad(t, n)
                              : e.runInContext(() => a(t, n)),
                          );
                        }),
                      ).pipe(Ki(), _E());
                })(t, n, r).pipe(
                  Ae((i) =>
                    i
                      ? this.configLoader.loadChildren(t, n).pipe(
                          Ee((o) => {
                            (n._loadedRoutes = o.routes),
                              (n._loadedInjector = o.injector);
                          }),
                        )
                      : (function yV(e) {
                          return $i(mE(!1, 3));
                        })(),
                  ),
                )
            : A({ routes: [], injector: t });
        }
      }
      function AV(e) {
        const t = e.value.routeConfig;
        return t && "" === t.path;
      }
      function CE(e) {
        const t = [],
          n = new Set();
        for (const r of e) {
          if (!AV(r)) {
            t.push(r);
            continue;
          }
          const i = t.find((o) => r.value.routeConfig === o.value.routeConfig);
          void 0 !== i ? (i.children.push(...r.children), n.add(i)) : t.push(r);
        }
        for (const r of n) {
          const i = CE(r.children);
          t.push(new Rn(r.value, i));
        }
        return t.filter((r) => !n.has(r));
      }
      function IE(e) {
        return e.data || {};
      }
      function ME(e) {
        return e.resolve || {};
      }
      function SE(e) {
        return "string" == typeof e.title || null === e.title;
      }
      function up(e) {
        return Ft((t) => {
          const n = e(t);
          return n ? Se(n).pipe(U(() => t)) : A(t);
        });
      }
      const Qi = new E("ROUTES");
      let dp = (() => {
        class e {
          constructor() {
            (this.componentLoaders = new WeakMap()),
              (this.childrenLoaders = new WeakMap()),
              (this.compiler = C(o0));
          }
          loadComponent(n) {
            if (this.componentLoaders.get(n))
              return this.componentLoaders.get(n);
            if (n._loadedComponent) return A(n._loadedComponent);
            this.onLoadStartListener && this.onLoadStartListener(n);
            const r = er(n.loadComponent()).pipe(
                U(xE),
                Ee((o) => {
                  this.onLoadEndListener && this.onLoadEndListener(n),
                    (n._loadedComponent = o);
                }),
                ji(() => {
                  this.componentLoaders.delete(n);
                }),
              ),
              i = new Lw(r, () => new Te()).pipe(zh());
            return this.componentLoaders.set(n, i), i;
          }
          loadChildren(n, r) {
            if (this.childrenLoaders.get(r)) return this.childrenLoaders.get(r);
            if (r._loadedRoutes)
              return A({
                routes: r._loadedRoutes,
                injector: r._loadedInjector,
              });
            this.onLoadStartListener && this.onLoadStartListener(r);
            const o = (function LV(e, t, n, r) {
                return er(e.loadChildren()).pipe(
                  U(xE),
                  Ae((i) =>
                    i instanceof u_ || Array.isArray(i)
                      ? A(i)
                      : Se(t.compileModuleAsync(i)),
                  ),
                  U((i) => {
                    r && r(e);
                    let o,
                      s,
                      a = !1;
                    return (
                      Array.isArray(i)
                        ? ((s = i), !0)
                        : ((o = i.create(n).injector),
                          (s = o
                            .get(Qi, [], { optional: !0, self: !0 })
                            .flat())),
                      { routes: s.map(ap), injector: o }
                    );
                  }),
                );
              })(r, this.compiler, n, this.onLoadEndListener).pipe(
                ji(() => {
                  this.childrenLoaders.delete(r);
                }),
              ),
              s = new Lw(o, () => new Te()).pipe(zh());
            return this.childrenLoaders.set(r, s), s;
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      function xE(e) {
        return (function jV(e) {
          return e && "object" == typeof e && "default" in e;
        })(e)
          ? e.default
          : e;
      }
      let gl = (() => {
        class e {
          get hasRequestedNavigation() {
            return 0 !== this.navigationId;
          }
          constructor() {
            (this.currentNavigation = null),
              (this.currentTransition = null),
              (this.lastSuccessfulNavigation = null),
              (this.events = new Te()),
              (this.transitionAbortSubject = new Te()),
              (this.configLoader = C(dp)),
              (this.environmentInjector = C(mt)),
              (this.urlSerializer = C(vs)),
              (this.rootContexts = C(Is)),
              (this.inputBindingEnabled = null !== C(dl, { optional: !0 })),
              (this.navigationId = 0),
              (this.afterPreactivation = () => A(void 0)),
              (this.rootComponentType = null),
              (this.configLoader.onLoadEndListener = (i) =>
                this.events.next(new AB(i))),
              (this.configLoader.onLoadStartListener = (i) =>
                this.events.next(new TB(i)));
          }
          complete() {
            this.transitions?.complete();
          }
          handleNavigationRequest(n) {
            const r = ++this.navigationId;
            this.transitions?.next({ ...this.transitions.value, ...n, id: r });
          }
          setupNavigations(n, r, i) {
            return (
              (this.transitions = new lt({
                id: 0,
                currentUrlTree: r,
                currentRawUrl: r,
                currentBrowserUrl: r,
                extractedUrl: n.urlHandlingStrategy.extract(r),
                urlAfterRedirects: n.urlHandlingStrategy.extract(r),
                rawUrl: r,
                extras: {},
                resolve: null,
                reject: null,
                promise: Promise.resolve(!0),
                source: Es,
                restoredState: null,
                currentSnapshot: i.snapshot,
                targetSnapshot: null,
                currentRouterState: i,
                targetRouterState: null,
                guards: { canActivateChecks: [], canDeactivateChecks: [] },
                guardsResult: null,
              })),
              this.transitions.pipe(
                Gt((o) => 0 !== o.id),
                U((o) => ({
                  ...o,
                  extractedUrl: n.urlHandlingStrategy.extract(o.rawUrl),
                })),
                Ft((o) => {
                  this.currentTransition = o;
                  let s = !1,
                    a = !1;
                  return A(o).pipe(
                    Ee((c) => {
                      this.currentNavigation = {
                        id: c.id,
                        initialUrl: c.rawUrl,
                        extractedUrl: c.extractedUrl,
                        trigger: c.source,
                        extras: c.extras,
                        previousNavigation: this.lastSuccessfulNavigation
                          ? {
                              ...this.lastSuccessfulNavigation,
                              previousNavigation: null,
                            }
                          : null,
                      };
                    }),
                    Ft((c) => {
                      const l = c.currentBrowserUrl.toString(),
                        u =
                          !n.navigated ||
                          c.extractedUrl.toString() !== l ||
                          l !== c.currentUrlTree.toString();
                      if (
                        !u &&
                        "reload" !==
                          (c.extras.onSameUrlNavigation ??
                            n.onSameUrlNavigation)
                      ) {
                        const f = "";
                        return (
                          this.events.next(
                            new zi(
                              c.id,
                              this.urlSerializer.serialize(c.rawUrl),
                              f,
                              0,
                            ),
                          ),
                          c.resolve(null),
                          Zt
                        );
                      }
                      if (n.urlHandlingStrategy.shouldProcessUrl(c.rawUrl))
                        return A(c).pipe(
                          Ft((f) => {
                            const h = this.transitions?.getValue();
                            return (
                              this.events.next(
                                new cl(
                                  f.id,
                                  this.urlSerializer.serialize(f.extractedUrl),
                                  f.source,
                                  f.restoredState,
                                ),
                              ),
                              h !== this.transitions?.getValue()
                                ? Zt
                                : Promise.resolve(f)
                            );
                          }),
                          (function NV(e, t, n, r, i, o) {
                            return Ae((s) =>
                              (function SV(e, t, n, r, i, o, s = "emptyOnly") {
                                return new xV(e, t, n, r, i, s, o).recognize();
                              })(e, t, n, r, s.extractedUrl, i, o).pipe(
                                U(({ state: a, tree: c }) => ({
                                  ...s,
                                  targetSnapshot: a,
                                  urlAfterRedirects: c,
                                })),
                              ),
                            );
                          })(
                            this.environmentInjector,
                            this.configLoader,
                            this.rootComponentType,
                            n.config,
                            this.urlSerializer,
                            n.paramsInheritanceStrategy,
                          ),
                          Ee((f) => {
                            (o.targetSnapshot = f.targetSnapshot),
                              (o.urlAfterRedirects = f.urlAfterRedirects),
                              (this.currentNavigation = {
                                ...this.currentNavigation,
                                finalUrl: f.urlAfterRedirects,
                              });
                            const h = new oE(
                              f.id,
                              this.urlSerializer.serialize(f.extractedUrl),
                              this.urlSerializer.serialize(f.urlAfterRedirects),
                              f.targetSnapshot,
                            );
                            this.events.next(h);
                          }),
                        );
                      if (
                        u &&
                        n.urlHandlingStrategy.shouldProcessUrl(c.currentRawUrl)
                      ) {
                        const {
                            id: f,
                            extractedUrl: h,
                            source: p,
                            restoredState: m,
                            extras: g,
                          } = c,
                          y = new cl(f, this.urlSerializer.serialize(h), p, m);
                        this.events.next(y);
                        const b = lE(0, this.rootComponentType).snapshot;
                        return (
                          (this.currentTransition = o =
                            {
                              ...c,
                              targetSnapshot: b,
                              urlAfterRedirects: h,
                              extras: {
                                ...g,
                                skipLocationChange: !1,
                                replaceUrl: !1,
                              },
                            }),
                          A(o)
                        );
                      }
                      {
                        const f = "";
                        return (
                          this.events.next(
                            new zi(
                              c.id,
                              this.urlSerializer.serialize(c.extractedUrl),
                              f,
                              1,
                            ),
                          ),
                          c.resolve(null),
                          Zt
                        );
                      }
                    }),
                    Ee((c) => {
                      const l = new IB(
                        c.id,
                        this.urlSerializer.serialize(c.extractedUrl),
                        this.urlSerializer.serialize(c.urlAfterRedirects),
                        c.targetSnapshot,
                      );
                      this.events.next(l);
                    }),
                    U(
                      (c) => (
                        (this.currentTransition = o =
                          {
                            ...c,
                            guards: QB(
                              c.targetSnapshot,
                              c.currentSnapshot,
                              this.rootContexts,
                            ),
                          }),
                        o
                      ),
                    ),
                    (function aV(e, t) {
                      return Ae((n) => {
                        const {
                          targetSnapshot: r,
                          currentSnapshot: i,
                          guards: {
                            canActivateChecks: o,
                            canDeactivateChecks: s,
                          },
                        } = n;
                        return 0 === s.length && 0 === o.length
                          ? A({ ...n, guardsResult: !0 })
                          : (function cV(e, t, n, r) {
                              return Se(e).pipe(
                                Ae((i) =>
                                  (function pV(e, t, n, r, i) {
                                    const o =
                                      t && t.routeConfig
                                        ? t.routeConfig.canDeactivate
                                        : null;
                                    return o && 0 !== o.length
                                      ? A(
                                          o.map((a) => {
                                            const c = Ss(t) ?? i,
                                              l = Wi(a, c);
                                            return er(
                                              (function iV(e) {
                                                return e && As(e.canDeactivate);
                                              })(l)
                                                ? l.canDeactivate(e, t, n, r)
                                                : c.runInContext(() =>
                                                    l(e, t, n, r),
                                                  ),
                                            ).pipe(Sr());
                                          }),
                                        ).pipe(Ki())
                                      : A(!0);
                                  })(i.component, i.route, n, t, r),
                                ),
                                Sr((i) => !0 !== i, !0),
                              );
                            })(s, r, i, e).pipe(
                              Ae((a) =>
                                a &&
                                (function eV(e) {
                                  return "boolean" == typeof e;
                                })(a)
                                  ? (function lV(e, t, n, r) {
                                      return Se(t).pipe(
                                        Li((i) =>
                                          el(
                                            (function dV(e, t) {
                                              return (
                                                null !== e && t && t(new NB(e)),
                                                A(!0)
                                              );
                                            })(i.route.parent, r),
                                            (function uV(e, t) {
                                              return (
                                                null !== e && t && t(new OB(e)),
                                                A(!0)
                                              );
                                            })(i.route, r),
                                            (function hV(e, t, n) {
                                              const r = t[t.length - 1],
                                                o = t
                                                  .slice(0, t.length - 1)
                                                  .reverse()
                                                  .map((s) =>
                                                    (function YB(e) {
                                                      const t = e.routeConfig
                                                        ? e.routeConfig
                                                            .canActivateChild
                                                        : null;
                                                      return t && 0 !== t.length
                                                        ? { node: e, guards: t }
                                                        : null;
                                                    })(s),
                                                  )
                                                  .filter((s) => null !== s)
                                                  .map((s) =>
                                                    Fw(() =>
                                                      A(
                                                        s.guards.map((c) => {
                                                          const l =
                                                              Ss(s.node) ?? n,
                                                            u = Wi(c, l);
                                                          return er(
                                                            (function rV(e) {
                                                              return (
                                                                e &&
                                                                As(
                                                                  e.canActivateChild,
                                                                )
                                                              );
                                                            })(u)
                                                              ? u.canActivateChild(
                                                                  r,
                                                                  e,
                                                                )
                                                              : l.runInContext(
                                                                  () => u(r, e),
                                                                ),
                                                          ).pipe(Sr());
                                                        }),
                                                      ).pipe(Ki()),
                                                    ),
                                                  );
                                              return A(o).pipe(Ki());
                                            })(e, i.path, n),
                                            (function fV(e, t, n) {
                                              const r = t.routeConfig
                                                ? t.routeConfig.canActivate
                                                : null;
                                              if (!r || 0 === r.length)
                                                return A(!0);
                                              const i = r.map((o) =>
                                                Fw(() => {
                                                  const s = Ss(t) ?? n,
                                                    a = Wi(o, s);
                                                  return er(
                                                    (function nV(e) {
                                                      return (
                                                        e && As(e.canActivate)
                                                      );
                                                    })(a)
                                                      ? a.canActivate(t, e)
                                                      : s.runInContext(() =>
                                                          a(t, e),
                                                        ),
                                                  ).pipe(Sr());
                                                }),
                                              );
                                              return A(i).pipe(Ki());
                                            })(e, i.route, n),
                                          ),
                                        ),
                                        Sr((i) => !0 !== i, !0),
                                      );
                                    })(r, o, e, t)
                                  : A(a),
                              ),
                              U((a) => ({ ...n, guardsResult: a })),
                            );
                      });
                    })(this.environmentInjector, (c) => this.events.next(c)),
                    Ee((c) => {
                      if (
                        ((o.guardsResult = c.guardsResult), Tr(c.guardsResult))
                      )
                        throw pE(0, c.guardsResult);
                      const l = new MB(
                        c.id,
                        this.urlSerializer.serialize(c.extractedUrl),
                        this.urlSerializer.serialize(c.urlAfterRedirects),
                        c.targetSnapshot,
                        !!c.guardsResult,
                      );
                      this.events.next(l);
                    }),
                    Gt(
                      (c) =>
                        !!c.guardsResult ||
                        (this.cancelNavigationTransition(c, "", 3), !1),
                    ),
                    up((c) => {
                      if (c.guards.canActivateChecks.length)
                        return A(c).pipe(
                          Ee((l) => {
                            const u = new SB(
                              l.id,
                              this.urlSerializer.serialize(l.extractedUrl),
                              this.urlSerializer.serialize(l.urlAfterRedirects),
                              l.targetSnapshot,
                            );
                            this.events.next(u);
                          }),
                          Ft((l) => {
                            let u = !1;
                            return A(l).pipe(
                              (function RV(e, t) {
                                return Ae((n) => {
                                  const {
                                    targetSnapshot: r,
                                    guards: { canActivateChecks: i },
                                  } = n;
                                  if (!i.length) return A(n);
                                  let o = 0;
                                  return Se(i).pipe(
                                    Li((s) =>
                                      (function OV(e, t, n, r) {
                                        const i = e.routeConfig,
                                          o = e._resolve;
                                        return (
                                          void 0 !== i?.title &&
                                            !SE(i) &&
                                            (o[bs] = i.title),
                                          (function PV(e, t, n, r) {
                                            const i = (function kV(e) {
                                              return [
                                                ...Object.keys(e),
                                                ...Object.getOwnPropertySymbols(
                                                  e,
                                                ),
                                              ];
                                            })(e);
                                            if (0 === i.length) return A({});
                                            const o = {};
                                            return Se(i).pipe(
                                              Ae((s) =>
                                                (function FV(e, t, n, r) {
                                                  const i = Ss(t) ?? r,
                                                    o = Wi(e, i);
                                                  return er(
                                                    o.resolve
                                                      ? o.resolve(t, n)
                                                      : i.runInContext(() =>
                                                          o(t, n),
                                                        ),
                                                  );
                                                })(e[s], t, n, r).pipe(
                                                  Sr(),
                                                  Ee((a) => {
                                                    o[s] = a;
                                                  }),
                                                ),
                                              ),
                                              qh(1),
                                              (function Qj(e) {
                                                return U(() => e);
                                              })(o),
                                              Jn((s) => (vE(s) ? Zt : $i(s))),
                                            );
                                          })(o, e, t, r).pipe(
                                            U(
                                              (s) => (
                                                (e._resolvedData = s),
                                                (e.data = uE(e, n).resolve),
                                                i &&
                                                  SE(i) &&
                                                  (e.data[bs] = i.title),
                                                null
                                              ),
                                            ),
                                          )
                                        );
                                      })(s.route, r, e, t),
                                    ),
                                    Ee(() => o++),
                                    qh(1),
                                    Ae((s) => (o === i.length ? A(n) : Zt)),
                                  );
                                });
                              })(
                                n.paramsInheritanceStrategy,
                                this.environmentInjector,
                              ),
                              Ee({
                                next: () => (u = !0),
                                complete: () => {
                                  u ||
                                    this.cancelNavigationTransition(l, "", 2);
                                },
                              }),
                            );
                          }),
                          Ee((l) => {
                            const u = new xB(
                              l.id,
                              this.urlSerializer.serialize(l.extractedUrl),
                              this.urlSerializer.serialize(l.urlAfterRedirects),
                              l.targetSnapshot,
                            );
                            this.events.next(u);
                          }),
                        );
                    }),
                    up((c) => {
                      const l = (u) => {
                        const d = [];
                        u.routeConfig?.loadComponent &&
                          !u.routeConfig._loadedComponent &&
                          d.push(
                            this.configLoader.loadComponent(u.routeConfig).pipe(
                              Ee((f) => {
                                u.component = f;
                              }),
                              U(() => {}),
                            ),
                          );
                        for (const f of u.children) d.push(...l(f));
                        return d;
                      };
                      return Xc(l(c.targetSnapshot.root)).pipe(tl(), Nn(1));
                    }),
                    up(() => this.afterPreactivation()),
                    U((c) => {
                      const l = (function BB(e, t, n) {
                        const r = Ms(e, t._root, n ? n._root : void 0);
                        return new cE(r, t);
                      })(
                        n.routeReuseStrategy,
                        c.targetSnapshot,
                        c.currentRouterState,
                      );
                      return (
                        (this.currentTransition = o =
                          { ...c, targetRouterState: l }),
                        o
                      );
                    }),
                    Ee(() => {
                      this.events.next(new Xh());
                    }),
                    ((e, t, n, r) =>
                      U(
                        (i) => (
                          new ZB(
                            t,
                            i.targetRouterState,
                            i.currentRouterState,
                            n,
                            r,
                          ).activate(e),
                          i
                        ),
                      ))(
                      this.rootContexts,
                      n.routeReuseStrategy,
                      (c) => this.events.next(c),
                      this.inputBindingEnabled,
                    ),
                    Nn(1),
                    Ee({
                      next: (c) => {
                        (s = !0),
                          (this.lastSuccessfulNavigation =
                            this.currentNavigation),
                          this.events.next(
                            new tr(
                              c.id,
                              this.urlSerializer.serialize(c.extractedUrl),
                              this.urlSerializer.serialize(c.urlAfterRedirects),
                            ),
                          ),
                          n.titleStrategy?.updateTitle(
                            c.targetRouterState.snapshot,
                          ),
                          c.resolve(!0);
                      },
                      complete: () => {
                        s = !0;
                      },
                    }),
                    Gh(
                      this.transitionAbortSubject.pipe(
                        Ee((c) => {
                          throw c;
                        }),
                      ),
                    ),
                    ji(() => {
                      s || a || this.cancelNavigationTransition(o, "", 1),
                        this.currentNavigation?.id === o.id &&
                          (this.currentNavigation = null);
                    }),
                    Jn((c) => {
                      if (((a = !0), gE(c)))
                        this.events.next(
                          new Cs(
                            o.id,
                            this.urlSerializer.serialize(o.extractedUrl),
                            c.message,
                            c.cancellationCode,
                          ),
                        ),
                          (function UB(e) {
                            return gE(e) && Tr(e.url);
                          })(c)
                            ? this.events.next(new Jh(c.url))
                            : o.resolve(!1);
                      else {
                        this.events.next(
                          new ll(
                            o.id,
                            this.urlSerializer.serialize(o.extractedUrl),
                            c,
                            o.targetSnapshot ?? void 0,
                          ),
                        );
                        try {
                          o.resolve(n.errorHandler(c));
                        } catch (l) {
                          o.reject(l);
                        }
                      }
                      return Zt;
                    }),
                  );
                }),
              )
            );
          }
          cancelNavigationTransition(n, r, i) {
            const o = new Cs(
              n.id,
              this.urlSerializer.serialize(n.extractedUrl),
              r,
              i,
            );
            this.events.next(o), n.resolve(!1);
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      function TE(e) {
        return e !== Es;
      }
      let AE = (() => {
          class e {
            buildTitle(n) {
              let r,
                i = n.root;
              for (; void 0 !== i; )
                (r = this.getResolvedTitleForRoute(i) ?? r),
                  (i = i.children.find((o) => o.outlet === $));
              return r;
            }
            getResolvedTitleForRoute(n) {
              return n.data[bs];
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵprov = S({
                token: e,
                factory: function () {
                  return C(BV);
                },
                providedIn: "root",
              });
            }
          }
          return e;
        })(),
        BV = (() => {
          class e extends AE {
            constructor(n) {
              super(), (this.title = n);
            }
            updateTitle(n) {
              const r = this.buildTitle(n);
              void 0 !== r && this.title.setTitle(r);
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(xD));
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
            }
          }
          return e;
        })(),
        VV = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵprov = S({
                token: e,
                factory: function () {
                  return C(UV);
                },
                providedIn: "root",
              });
            }
          }
          return e;
        })();
      class $V {
        shouldDetach(t) {
          return !1;
        }
        store(t, n) {}
        shouldAttach(t) {
          return !1;
        }
        retrieve(t) {
          return null;
        }
        shouldReuseRoute(t, n) {
          return t.routeConfig === n.routeConfig;
        }
      }
      let UV = (() => {
        class e extends $V {
          static {
            this.ɵfac = (function () {
              let n;
              return function (i) {
                return (
                  n ||
                  (n = (function mg(e) {
                    return mn(() => {
                      const t = e.prototype.constructor,
                        n = t[gn] || xu(t),
                        r = Object.prototype;
                      let i = Object.getPrototypeOf(e.prototype).constructor;
                      for (; i && i !== r; ) {
                        const o = i[gn] || xu(i);
                        if (o && o !== n) return o;
                        i = Object.getPrototypeOf(i);
                      }
                      return (o) => new o();
                    });
                  })(e))
                )(i || e);
              };
            })();
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      const bl = new E("", { providedIn: "root", factory: () => ({}) });
      let HV = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵprov = S({
                token: e,
                factory: function () {
                  return C(zV);
                },
                providedIn: "root",
              });
            }
          }
          return e;
        })(),
        zV = (() => {
          class e {
            shouldProcessUrl(n) {
              return !0;
            }
            extract(n) {
              return n;
            }
            merge(n, r) {
              return n;
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
            }
          }
          return e;
        })();
      var Ns = (function (e) {
        return (
          (e[(e.COMPLETE = 0)] = "COMPLETE"),
          (e[(e.FAILED = 1)] = "FAILED"),
          (e[(e.REDIRECTING = 2)] = "REDIRECTING"),
          e
        );
      })(Ns || {});
      function NE(e, t) {
        e.events
          .pipe(
            Gt(
              (n) =>
                n instanceof tr ||
                n instanceof Cs ||
                n instanceof ll ||
                n instanceof zi,
            ),
            U((n) =>
              n instanceof tr || n instanceof zi
                ? Ns.COMPLETE
                : n instanceof Cs && (0 === n.code || 1 === n.code)
                ? Ns.REDIRECTING
                : Ns.FAILED,
            ),
            Gt((n) => n !== Ns.REDIRECTING),
            Nn(1),
          )
          .subscribe(() => {
            t();
          });
      }
      function qV(e) {
        throw e;
      }
      function GV(e, t, n) {
        return t.parse("/");
      }
      const WV = {
          paths: "exact",
          fragment: "ignored",
          matrixParams: "ignored",
          queryParams: "exact",
        },
        KV = {
          paths: "subset",
          fragment: "ignored",
          matrixParams: "ignored",
          queryParams: "subset",
        };
      let Pt = (() => {
        class e {
          get navigationId() {
            return this.navigationTransitions.navigationId;
          }
          get browserPageId() {
            return "computed" !== this.canceledNavigationResolution
              ? this.currentPageId
              : this.location.getState()?.ɵrouterPageId ?? this.currentPageId;
          }
          get events() {
            return this._events;
          }
          constructor() {
            (this.disposed = !1),
              (this.currentPageId = 0),
              (this.console = C(r0)),
              (this.isNgZoneEnabled = !1),
              (this._events = new Te()),
              (this.options = C(bl, { optional: !0 }) || {}),
              (this.pendingTasks = C(fc)),
              (this.errorHandler = this.options.errorHandler || qV),
              (this.malformedUriErrorHandler =
                this.options.malformedUriErrorHandler || GV),
              (this.navigated = !1),
              (this.lastSuccessfulId = -1),
              (this.urlHandlingStrategy = C(HV)),
              (this.routeReuseStrategy = C(VV)),
              (this.titleStrategy = C(AE)),
              (this.onSameUrlNavigation =
                this.options.onSameUrlNavigation || "ignore"),
              (this.paramsInheritanceStrategy =
                this.options.paramsInheritanceStrategy || "emptyOnly"),
              (this.urlUpdateStrategy =
                this.options.urlUpdateStrategy || "deferred"),
              (this.canceledNavigationResolution =
                this.options.canceledNavigationResolution || "replace"),
              (this.config = C(Qi, { optional: !0 })?.flat() ?? []),
              (this.navigationTransitions = C(gl)),
              (this.urlSerializer = C(vs)),
              (this.location = C(Uf)),
              (this.componentInputBindingEnabled = !!C(dl, { optional: !0 })),
              (this.eventsSubscription = new je()),
              (this.isNgZoneEnabled = C(W) instanceof W && W.isInAngularZone()),
              this.resetConfig(this.config),
              (this.currentUrlTree = new Hi()),
              (this.rawUrlTree = this.currentUrlTree),
              (this.browserUrlTree = this.currentUrlTree),
              (this.routerState = lE(0, null)),
              this.navigationTransitions
                .setupNavigations(this, this.currentUrlTree, this.routerState)
                .subscribe(
                  (n) => {
                    (this.lastSuccessfulId = n.id),
                      (this.currentPageId = this.browserPageId);
                  },
                  (n) => {
                    this.console.warn(`Unhandled Navigation Error: ${n}`);
                  },
                ),
              this.subscribeToNavigationEvents();
          }
          subscribeToNavigationEvents() {
            const n = this.navigationTransitions.events.subscribe((r) => {
              try {
                const { currentTransition: i } = this.navigationTransitions;
                if (null === i) return void (RE(r) && this._events.next(r));
                if (r instanceof cl)
                  TE(i.source) && (this.browserUrlTree = i.extractedUrl);
                else if (r instanceof zi) this.rawUrlTree = i.rawUrl;
                else if (r instanceof oE) {
                  if ("eager" === this.urlUpdateStrategy) {
                    if (!i.extras.skipLocationChange) {
                      const o = this.urlHandlingStrategy.merge(
                        i.urlAfterRedirects,
                        i.rawUrl,
                      );
                      this.setBrowserUrl(o, i);
                    }
                    this.browserUrlTree = i.urlAfterRedirects;
                  }
                } else if (r instanceof Xh)
                  (this.currentUrlTree = i.urlAfterRedirects),
                    (this.rawUrlTree = this.urlHandlingStrategy.merge(
                      i.urlAfterRedirects,
                      i.rawUrl,
                    )),
                    (this.routerState = i.targetRouterState),
                    "deferred" === this.urlUpdateStrategy &&
                      (i.extras.skipLocationChange ||
                        this.setBrowserUrl(this.rawUrlTree, i),
                      (this.browserUrlTree = i.urlAfterRedirects));
                else if (r instanceof Cs)
                  0 !== r.code && 1 !== r.code && (this.navigated = !0),
                    (3 === r.code || 2 === r.code) && this.restoreHistory(i);
                else if (r instanceof Jh) {
                  const o = this.urlHandlingStrategy.merge(
                      r.url,
                      i.currentRawUrl,
                    ),
                    s = {
                      skipLocationChange: i.extras.skipLocationChange,
                      replaceUrl:
                        "eager" === this.urlUpdateStrategy || TE(i.source),
                    };
                  this.scheduleNavigation(o, Es, null, s, {
                    resolve: i.resolve,
                    reject: i.reject,
                    promise: i.promise,
                  });
                }
                r instanceof ll && this.restoreHistory(i, !0),
                  r instanceof tr && (this.navigated = !0),
                  RE(r) && this._events.next(r);
              } catch (i) {
                this.navigationTransitions.transitionAbortSubject.next(i);
              }
            });
            this.eventsSubscription.add(n);
          }
          resetRootComponentType(n) {
            (this.routerState.root.component = n),
              (this.navigationTransitions.rootComponentType = n);
          }
          initialNavigation() {
            if (
              (this.setUpLocationChangeListener(),
              !this.navigationTransitions.hasRequestedNavigation)
            ) {
              const n = this.location.getState();
              this.navigateToSyncWithBrowser(this.location.path(!0), Es, n);
            }
          }
          setUpLocationChangeListener() {
            this.locationSubscription ||
              (this.locationSubscription = this.location.subscribe((n) => {
                const r = "popstate" === n.type ? "popstate" : "hashchange";
                "popstate" === r &&
                  setTimeout(() => {
                    this.navigateToSyncWithBrowser(n.url, r, n.state);
                  }, 0);
              }));
          }
          navigateToSyncWithBrowser(n, r, i) {
            const o = { replaceUrl: !0 },
              s = i?.navigationId ? i : null;
            if (i) {
              const c = { ...i };
              delete c.navigationId,
                delete c.ɵrouterPageId,
                0 !== Object.keys(c).length && (o.state = c);
            }
            const a = this.parseUrl(n);
            this.scheduleNavigation(a, r, s, o);
          }
          get url() {
            return this.serializeUrl(this.currentUrlTree);
          }
          getCurrentNavigation() {
            return this.navigationTransitions.currentNavigation;
          }
          get lastSuccessfulNavigation() {
            return this.navigationTransitions.lastSuccessfulNavigation;
          }
          resetConfig(n) {
            (this.config = n.map(ap)),
              (this.navigated = !1),
              (this.lastSuccessfulId = -1);
          }
          ngOnDestroy() {
            this.dispose();
          }
          dispose() {
            this.navigationTransitions.complete(),
              this.locationSubscription &&
                (this.locationSubscription.unsubscribe(),
                (this.locationSubscription = void 0)),
              (this.disposed = !0),
              this.eventsSubscription.unsubscribe();
          }
          createUrlTree(n, r = {}) {
            const {
                relativeTo: i,
                queryParams: o,
                fragment: s,
                queryParamsHandling: a,
                preserveFragment: c,
              } = r,
              l = c ? this.currentUrlTree.fragment : s;
            let d,
              u = null;
            switch (a) {
              case "merge":
                u = { ...this.currentUrlTree.queryParams, ...o };
                break;
              case "preserve":
                u = this.currentUrlTree.queryParams;
                break;
              default:
                u = o || null;
            }
            null !== u && (u = this.removeEmptyProps(u));
            try {
              d = Xw(i ? i.snapshot : this.routerState.snapshot.root);
            } catch {
              ("string" != typeof n[0] || !n[0].startsWith("/")) && (n = []),
                (d = this.currentUrlTree.root);
            }
            return Jw(d, n, u, l ?? null);
          }
          navigateByUrl(n, r = { skipLocationChange: !1 }) {
            const i = Tr(n) ? n : this.parseUrl(n),
              o = this.urlHandlingStrategy.merge(i, this.rawUrlTree);
            return this.scheduleNavigation(o, Es, null, r);
          }
          navigate(n, r = { skipLocationChange: !1 }) {
            return (
              (function ZV(e) {
                for (let t = 0; t < e.length; t++)
                  if (null == e[t]) throw new v(4008, !1);
              })(n),
              this.navigateByUrl(this.createUrlTree(n, r), r)
            );
          }
          serializeUrl(n) {
            return this.urlSerializer.serialize(n);
          }
          parseUrl(n) {
            let r;
            try {
              r = this.urlSerializer.parse(n);
            } catch (i) {
              r = this.malformedUriErrorHandler(i, this.urlSerializer, n);
            }
            return r;
          }
          isActive(n, r) {
            let i;
            if (((i = !0 === r ? { ...WV } : !1 === r ? { ...KV } : r), Tr(n)))
              return Hw(this.currentUrlTree, n, i);
            const o = this.parseUrl(n);
            return Hw(this.currentUrlTree, o, i);
          }
          removeEmptyProps(n) {
            return Object.keys(n).reduce((r, i) => {
              const o = n[i];
              return null != o && (r[i] = o), r;
            }, {});
          }
          scheduleNavigation(n, r, i, o, s) {
            if (this.disposed) return Promise.resolve(!1);
            let a, c, l;
            s
              ? ((a = s.resolve), (c = s.reject), (l = s.promise))
              : (l = new Promise((d, f) => {
                  (a = d), (c = f);
                }));
            const u = this.pendingTasks.add();
            return (
              NE(this, () => {
                queueMicrotask(() => this.pendingTasks.remove(u));
              }),
              this.navigationTransitions.handleNavigationRequest({
                source: r,
                restoredState: i,
                currentUrlTree: this.currentUrlTree,
                currentRawUrl: this.currentUrlTree,
                currentBrowserUrl: this.browserUrlTree,
                rawUrl: n,
                extras: o,
                resolve: a,
                reject: c,
                promise: l,
                currentSnapshot: this.routerState.snapshot,
                currentRouterState: this.routerState,
              }),
              l.catch((d) => Promise.reject(d))
            );
          }
          setBrowserUrl(n, r) {
            const i = this.urlSerializer.serialize(n);
            if (this.location.isCurrentPathEqualTo(i) || r.extras.replaceUrl) {
              const s = {
                ...r.extras.state,
                ...this.generateNgRouterState(r.id, this.browserPageId),
              };
              this.location.replaceState(i, "", s);
            } else {
              const o = {
                ...r.extras.state,
                ...this.generateNgRouterState(r.id, this.browserPageId + 1),
              };
              this.location.go(i, "", o);
            }
          }
          restoreHistory(n, r = !1) {
            if ("computed" === this.canceledNavigationResolution) {
              const o = this.currentPageId - this.browserPageId;
              0 !== o
                ? this.location.historyGo(o)
                : this.currentUrlTree ===
                    this.getCurrentNavigation()?.finalUrl &&
                  0 === o &&
                  (this.resetState(n),
                  (this.browserUrlTree = n.currentUrlTree),
                  this.resetUrlToCurrentUrlTree());
            } else
              "replace" === this.canceledNavigationResolution &&
                (r && this.resetState(n), this.resetUrlToCurrentUrlTree());
          }
          resetState(n) {
            (this.routerState = n.currentRouterState),
              (this.currentUrlTree = n.currentUrlTree),
              (this.rawUrlTree = this.urlHandlingStrategy.merge(
                this.currentUrlTree,
                n.rawUrl,
              ));
          }
          resetUrlToCurrentUrlTree() {
            this.location.replaceState(
              this.urlSerializer.serialize(this.rawUrlTree),
              "",
              this.generateNgRouterState(
                this.lastSuccessfulId,
                this.currentPageId,
              ),
            );
          }
          generateNgRouterState(n, r) {
            return "computed" === this.canceledNavigationResolution
              ? { navigationId: n, ɵrouterPageId: r }
              : { navigationId: n };
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      function RE(e) {
        return !(e instanceof Xh || e instanceof Jh);
      }
      class OE {}
      let XV = (() => {
        class e {
          constructor(n, r, i, o, s) {
            (this.router = n),
              (this.injector = i),
              (this.preloadingStrategy = o),
              (this.loader = s);
          }
          setUpPreloading() {
            this.subscription = this.router.events
              .pipe(
                Gt((n) => n instanceof tr),
                Li(() => this.preload()),
              )
              .subscribe(() => {});
          }
          preload() {
            return this.processRoutes(this.injector, this.router.config);
          }
          ngOnDestroy() {
            this.subscription && this.subscription.unsubscribe();
          }
          processRoutes(n, r) {
            const i = [];
            for (const o of r) {
              o.providers &&
                !o._injector &&
                (o._injector = lf(o.providers, n, `Route: ${o.path}`));
              const s = o._injector ?? n,
                a = o._loadedInjector ?? s;
              ((o.loadChildren && !o._loadedRoutes && void 0 === o.canLoad) ||
                (o.loadComponent && !o._loadedComponent)) &&
                i.push(this.preloadConfig(s, o)),
                (o.children || o._loadedRoutes) &&
                  i.push(this.processRoutes(a, o.children ?? o._loadedRoutes));
            }
            return Se(i).pipe(Lr());
          }
          preloadConfig(n, r) {
            return this.preloadingStrategy.preload(r, () => {
              let i;
              i =
                r.loadChildren && void 0 === r.canLoad
                  ? this.loader.loadChildren(n, r)
                  : A(null);
              const o = i.pipe(
                Ae((s) =>
                  null === s
                    ? A(void 0)
                    : ((r._loadedRoutes = s.routes),
                      (r._loadedInjector = s.injector),
                      this.processRoutes(s.injector ?? n, s.routes)),
                ),
              );
              return r.loadComponent && !r._loadedComponent
                ? Se([o, this.loader.loadComponent(r)]).pipe(Lr())
                : o;
            });
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(Pt), D(o0), D(mt), D(OE), D(dp));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      const hp = new E("");
      let PE = (() => {
        class e {
          constructor(n, r, i, o, s = {}) {
            (this.urlSerializer = n),
              (this.transitions = r),
              (this.viewportScroller = i),
              (this.zone = o),
              (this.options = s),
              (this.lastId = 0),
              (this.lastSource = "imperative"),
              (this.restoredId = 0),
              (this.store = {}),
              (s.scrollPositionRestoration =
                s.scrollPositionRestoration || "disabled"),
              (s.anchorScrolling = s.anchorScrolling || "disabled");
          }
          init() {
            "disabled" !== this.options.scrollPositionRestoration &&
              this.viewportScroller.setHistoryScrollRestoration("manual"),
              (this.routerEventsSubscription = this.createScrollEvents()),
              (this.scrollEventsSubscription = this.consumeScrollEvents());
          }
          createScrollEvents() {
            return this.transitions.events.subscribe((n) => {
              n instanceof cl
                ? ((this.store[this.lastId] =
                    this.viewportScroller.getScrollPosition()),
                  (this.lastSource = n.navigationTrigger),
                  (this.restoredId = n.restoredState
                    ? n.restoredState.navigationId
                    : 0))
                : n instanceof tr
                ? ((this.lastId = n.id),
                  this.scheduleScrollEvent(
                    n,
                    this.urlSerializer.parse(n.urlAfterRedirects).fragment,
                  ))
                : n instanceof zi &&
                  0 === n.code &&
                  ((this.lastSource = void 0),
                  (this.restoredId = 0),
                  this.scheduleScrollEvent(
                    n,
                    this.urlSerializer.parse(n.url).fragment,
                  ));
            });
          }
          consumeScrollEvents() {
            return this.transitions.events.subscribe((n) => {
              n instanceof sE &&
                (n.position
                  ? "top" === this.options.scrollPositionRestoration
                    ? this.viewportScroller.scrollToPosition([0, 0])
                    : "enabled" === this.options.scrollPositionRestoration &&
                      this.viewportScroller.scrollToPosition(n.position)
                  : n.anchor && "enabled" === this.options.anchorScrolling
                  ? this.viewportScroller.scrollToAnchor(n.anchor)
                  : "disabled" !== this.options.scrollPositionRestoration &&
                    this.viewportScroller.scrollToPosition([0, 0]));
            });
          }
          scheduleScrollEvent(n, r) {
            this.zone.runOutsideAngular(() => {
              setTimeout(() => {
                this.zone.run(() => {
                  this.transitions.events.next(
                    new sE(
                      n,
                      "popstate" === this.lastSource
                        ? this.store[this.restoredId]
                        : null,
                      r,
                    ),
                  );
                });
              }, 0);
            });
          }
          ngOnDestroy() {
            this.routerEventsSubscription?.unsubscribe(),
              this.scrollEventsSubscription?.unsubscribe();
          }
          static {
            this.ɵfac = function (r) {
              Id();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac });
          }
        }
        return e;
      })();
      function On(e, t) {
        return { ɵkind: e, ɵproviders: t };
      }
      function FE() {
        const e = C(bt);
        return (t) => {
          const n = e.get(_r);
          if (t !== n.components[0]) return;
          const r = e.get(Pt),
            i = e.get(LE);
          1 === e.get(pp) && r.initialNavigation(),
            e.get(jE, null, H.Optional)?.setUpPreloading(),
            e.get(hp, null, H.Optional)?.init(),
            r.resetRootComponentType(n.componentTypes[0]),
            i.closed || (i.next(), i.complete(), i.unsubscribe());
        };
      }
      const LE = new E("", { factory: () => new Te() }),
        pp = new E("", { providedIn: "root", factory: () => 1 }),
        jE = new E("");
      function n$(e) {
        return On(0, [
          { provide: jE, useExisting: XV },
          { provide: OE, useExisting: e },
        ]);
      }
      const BE = new E("ROUTER_FORROOT_GUARD"),
        i$ = [
          Uf,
          { provide: vs, useClass: Wh },
          Pt,
          Is,
          {
            provide: Gi,
            useFactory: function kE(e) {
              return e.routerState.root;
            },
            deps: [Pt],
          },
          dp,
          [],
        ];
      function o$() {
        return new f0("Router", Pt);
      }
      let VE = (() => {
        class e {
          constructor(n) {}
          static forRoot(n, r) {
            return {
              ngModule: e,
              providers: [
                i$,
                [],
                { provide: Qi, multi: !0, useValue: n },
                {
                  provide: BE,
                  useFactory: l$,
                  deps: [[Pt, new dr(), new Co()]],
                },
                { provide: bl, useValue: r || {} },
                r?.useHash
                  ? { provide: wr, useClass: WP }
                  : { provide: wr, useClass: H0 },
                {
                  provide: hp,
                  useFactory: () => {
                    const e = C(fF),
                      t = C(W),
                      n = C(bl),
                      r = C(gl),
                      i = C(vs);
                    return (
                      n.scrollOffset && e.setOffset(n.scrollOffset),
                      new PE(i, r, e, t, n)
                    );
                  },
                },
                r?.preloadingStrategy
                  ? n$(r.preloadingStrategy).ɵproviders
                  : [],
                { provide: f0, multi: !0, useFactory: o$ },
                r?.initialNavigation ? u$(r) : [],
                r?.bindToComponentInputs
                  ? On(8, [hE, { provide: dl, useExisting: hE }]).ɵproviders
                  : [],
                [
                  { provide: $E, useFactory: FE },
                  { provide: Af, multi: !0, useExisting: $E },
                ],
              ],
            };
          }
          static forChild(n) {
            return {
              ngModule: e,
              providers: [{ provide: Qi, multi: !0, useValue: n }],
            };
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(BE, 8));
            };
          }
          static {
            this.ɵmod = Be({ type: e });
          }
          static {
            this.ɵinj = Ne({});
          }
        }
        return e;
      })();
      function l$(e) {
        return "guarded";
      }
      function u$(e) {
        return [
          "disabled" === e.initialNavigation
            ? On(3, [
                {
                  provide: wf,
                  multi: !0,
                  useFactory: () => {
                    const t = C(Pt);
                    return () => {
                      t.setUpLocationChangeListener();
                    };
                  },
                },
                { provide: pp, useValue: 2 },
              ]).ɵproviders
            : [],
          "enabledBlocking" === e.initialNavigation
            ? On(2, [
                { provide: pp, useValue: 0 },
                {
                  provide: wf,
                  multi: !0,
                  deps: [bt],
                  useFactory: (t) => {
                    const n = t.get(qP, Promise.resolve());
                    return () =>
                      n.then(
                        () =>
                          new Promise((r) => {
                            const i = t.get(Pt),
                              o = t.get(LE);
                            NE(i, () => {
                              r(!0);
                            }),
                              (t.get(gl).afterPreactivation = () => (
                                r(!0), o.closed ? A(void 0) : o
                              )),
                              i.initialNavigation();
                          }),
                      );
                  },
                },
              ]).ɵproviders
            : [],
        ];
      }
      const $E = new E(""),
        f$ = [];
      let mp,
        h$ = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵmod = Be({ type: e });
            }
            static {
              this.ɵinj = Ne({ imports: [VE.forRoot(f$), VE] });
            }
          }
          return e;
        })(),
        p$ = (() => {
          class e {
            constructor(n) {
              (this.http = n), (this.baseUrl = "http://localhost:8000/api");
            }
            checkBackendStatus() {
              return this.http.get(`${this.baseUrl}/`);
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(Qc));
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
            }
          }
          return e;
        })();
      try {
        mp = typeof Intl < "u" && Intl.v8BreakIterator;
      } catch {
        mp = !1;
      }
      let Rs,
        gp,
        Ar = (() => {
          class e {
            constructor(n) {
              (this._platformId = n),
                (this.isBrowser = this._platformId
                  ? (function dF(e) {
                      return e === cD;
                    })(this._platformId)
                  : "object" == typeof document && !!document),
                (this.EDGE =
                  this.isBrowser && /(edge)/i.test(navigator.userAgent)),
                (this.TRIDENT =
                  this.isBrowser &&
                  /(msie|trident)/i.test(navigator.userAgent)),
                (this.BLINK =
                  this.isBrowser &&
                  !(!window.chrome && !mp) &&
                  typeof CSS < "u" &&
                  !this.EDGE &&
                  !this.TRIDENT),
                (this.WEBKIT =
                  this.isBrowser &&
                  /AppleWebKit/i.test(navigator.userAgent) &&
                  !this.BLINK &&
                  !this.EDGE &&
                  !this.TRIDENT),
                (this.IOS =
                  this.isBrowser &&
                  /iPad|iPhone|iPod/.test(navigator.userAgent) &&
                  !("MSStream" in window)),
                (this.FIREFOX =
                  this.isBrowser &&
                  /(firefox|minefield)/i.test(navigator.userAgent)),
                (this.ANDROID =
                  this.isBrowser &&
                  /android/i.test(navigator.userAgent) &&
                  !this.TRIDENT),
                (this.SAFARI =
                  this.isBrowser &&
                  /safari/i.test(navigator.userAgent) &&
                  this.WEBKIT);
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(zn));
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
            }
          }
          return e;
        })();
      function yl(e) {
        return (function m$() {
          if (null == Rs && typeof window < "u")
            try {
              window.addEventListener(
                "test",
                null,
                Object.defineProperty({}, "passive", { get: () => (Rs = !0) }),
              );
            } finally {
              Rs = Rs || !1;
            }
          return Rs;
        })()
          ? e
          : !!e.capture;
      }
      function Xi(e) {
        return e.composedPath ? e.composedPath()[0] : e.target;
      }
      class j$ extends je {
        constructor(t, n) {
          super();
        }
        schedule(t, n = 0) {
          return this;
        }
      }
      const _l = {
          setInterval(e, t, ...n) {
            const { delegate: r } = _l;
            return r?.setInterval
              ? r.setInterval(e, t, ...n)
              : setInterval(e, t, ...n);
          },
          clearInterval(e) {
            const { delegate: t } = _l;
            return (t?.clearInterval || clearInterval)(e);
          },
          delegate: void 0,
        },
        HE = { now: () => (HE.delegate || Date).now(), delegate: void 0 };
      class Os {
        constructor(t, n = Os.now) {
          (this.schedulerActionCtor = t), (this.now = n);
        }
        schedule(t, n = 0, r) {
          return new this.schedulerActionCtor(this, t).schedule(r, n);
        }
      }
      Os.now = HE.now;
      const $$ = new (class V$ extends Os {
        constructor(t, n = Os.now) {
          super(t, n), (this.actions = []), (this._active = !1);
        }
        flush(t) {
          const { actions: n } = this;
          if (this._active) return void n.push(t);
          let r;
          this._active = !0;
          do {
            if ((r = t.execute(t.state, t.delay))) break;
          } while ((t = n.shift()));
          if (((this._active = !1), r)) {
            for (; (t = n.shift()); ) t.unsubscribe();
            throw r;
          }
        }
      })(
        class B$ extends j$ {
          constructor(t, n) {
            super(t, n),
              (this.scheduler = t),
              (this.work = n),
              (this.pending = !1);
          }
          schedule(t, n = 0) {
            var r;
            if (this.closed) return this;
            this.state = t;
            const i = this.id,
              o = this.scheduler;
            return (
              null != i && (this.id = this.recycleAsyncId(o, i, n)),
              (this.pending = !0),
              (this.delay = n),
              (this.id =
                null !== (r = this.id) && void 0 !== r
                  ? r
                  : this.requestAsyncId(o, this.id, n)),
              this
            );
          }
          requestAsyncId(t, n, r = 0) {
            return _l.setInterval(t.flush.bind(t, this), r);
          }
          recycleAsyncId(t, n, r = 0) {
            if (null != r && this.delay === r && !1 === this.pending) return n;
            null != n && _l.clearInterval(n);
          }
          execute(t, n) {
            if (this.closed) return new Error("executing a cancelled action");
            this.pending = !1;
            const r = this._execute(t, n);
            if (r) return r;
            !1 === this.pending &&
              null != this.id &&
              (this.id = this.recycleAsyncId(this.scheduler, this.id, null));
          }
          _execute(t, n) {
            let i,
              r = !1;
            try {
              this.work(t);
            } catch (o) {
              (r = !0),
                (i = o || new Error("Scheduled action threw falsy error"));
            }
            if (r) return this.unsubscribe(), i;
          }
          unsubscribe() {
            if (!this.closed) {
              const { id: t, scheduler: n } = this,
                { actions: r } = n;
              (this.work = this.state = this.scheduler = null),
                (this.pending = !1),
                Fr(r, this),
                null != t && (this.id = this.recycleAsyncId(n, t, null)),
                (this.delay = null),
                super.unsubscribe();
            }
          }
        },
      );
      function qE(e) {
        return Gt((t, n) => e <= n);
      }
      function Ps(e) {
        return null != e && "false" != `${e}`;
      }
      function GE(e) {
        return Array.isArray(e) ? e : [e];
      }
      function ks(e) {
        return e instanceof gt ? e.nativeElement : e;
      }
      const WE = new Set();
      let Rr,
        H$ = (() => {
          class e {
            constructor(n, r) {
              (this._platform = n),
                (this._nonce = r),
                (this._matchMedia =
                  this._platform.isBrowser && window.matchMedia
                    ? window.matchMedia.bind(window)
                    : q$);
            }
            matchMedia(n) {
              return (
                (this._platform.WEBKIT || this._platform.BLINK) &&
                  (function z$(e, t) {
                    if (!WE.has(e))
                      try {
                        Rr ||
                          ((Rr = document.createElement("style")),
                          t && (Rr.nonce = t),
                          Rr.setAttribute("type", "text/css"),
                          document.head.appendChild(Rr)),
                          Rr.sheet &&
                            (Rr.sheet.insertRule(`@media ${e} {body{ }}`, 0),
                            WE.add(e));
                      } catch (n) {
                        console.error(n);
                      }
                  })(n, this._nonce),
                this._matchMedia(n)
              );
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(Ar), D(ad, 8));
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
            }
          }
          return e;
        })();
      function q$(e) {
        return {
          matches: "all" === e || "" === e,
          media: e,
          addListener: () => {},
          removeListener: () => {},
        };
      }
      let G$ = (() => {
        class e {
          constructor(n, r) {
            (this._mediaMatcher = n),
              (this._zone = r),
              (this._queries = new Map()),
              (this._destroySubject = new Te());
          }
          ngOnDestroy() {
            this._destroySubject.next(), this._destroySubject.complete();
          }
          isMatched(n) {
            return KE(GE(n)).some((i) => this._registerQuery(i).mql.matches);
          }
          observe(n) {
            let o = Xc(KE(GE(n)).map((s) => this._registerQuery(s).observable));
            return (
              (o = el(
                o.pipe(Nn(1)),
                o.pipe(
                  qE(1),
                  (function zE(e, t = $$) {
                    return De((n, r) => {
                      let i = null,
                        o = null,
                        s = null;
                      const a = () => {
                        if (i) {
                          i.unsubscribe(), (i = null);
                          const l = o;
                          (o = null), r.next(l);
                        }
                      };
                      function c() {
                        const l = s + e,
                          u = t.now();
                        if (u < l)
                          return (
                            (i = this.schedule(void 0, l - u)), void r.add(i)
                          );
                        a();
                      }
                      n.subscribe(
                        be(
                          r,
                          (l) => {
                            (o = l),
                              (s = t.now()),
                              i || ((i = t.schedule(c, e)), r.add(i));
                          },
                          () => {
                            a(), r.complete();
                          },
                          void 0,
                          () => {
                            o = i = null;
                          },
                        ),
                      );
                    });
                  })(0),
                ),
              )),
              o.pipe(
                U((s) => {
                  const a = { matches: !1, breakpoints: {} };
                  return (
                    s.forEach(({ matches: c, query: l }) => {
                      (a.matches = a.matches || c), (a.breakpoints[l] = c);
                    }),
                    a
                  );
                }),
              )
            );
          }
          _registerQuery(n) {
            if (this._queries.has(n)) return this._queries.get(n);
            const r = this._mediaMatcher.matchMedia(n),
              o = {
                observable: new pe((s) => {
                  const a = (c) => this._zone.run(() => s.next(c));
                  return (
                    r.addListener(a),
                    () => {
                      r.removeListener(a);
                    }
                  );
                }).pipe(
                  jw(r),
                  U(({ matches: s }) => ({ query: n, matches: s })),
                  Gh(this._destroySubject),
                ),
                mql: r,
              };
            return this._queries.set(n, o), o;
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(H$), D(W));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      function KE(e) {
        return e
          .map((t) => t.split(","))
          .reduce((t, n) => t.concat(n))
          .map((t) => t.trim());
      }
      function XE(e) {
        return 0 === e.buttons || 0 === e.detail;
      }
      function JE(e) {
        const t =
          (e.touches && e.touches[0]) ||
          (e.changedTouches && e.changedTouches[0]);
        return !(
          !t ||
          -1 !== t.identifier ||
          (null != t.radiusX && 1 !== t.radiusX) ||
          (null != t.radiusY && 1 !== t.radiusY)
        );
      }
      const nU = new E("cdk-input-modality-detector-options"),
        rU = { ignoreKeys: [18, 17, 224, 91, 16] },
        Ji = yl({ passive: !0, capture: !0 });
      let iU = (() => {
        class e {
          get mostRecentModality() {
            return this._modality.value;
          }
          constructor(n, r, i, o) {
            (this._platform = n),
              (this._mostRecentTarget = null),
              (this._modality = new lt(null)),
              (this._lastTouchMs = 0),
              (this._onKeydown = (s) => {
                this._options?.ignoreKeys?.some((a) => a === s.keyCode) ||
                  (this._modality.next("keyboard"),
                  (this._mostRecentTarget = Xi(s)));
              }),
              (this._onMousedown = (s) => {
                Date.now() - this._lastTouchMs < 650 ||
                  (this._modality.next(XE(s) ? "keyboard" : "mouse"),
                  (this._mostRecentTarget = Xi(s)));
              }),
              (this._onTouchstart = (s) => {
                JE(s)
                  ? this._modality.next("keyboard")
                  : ((this._lastTouchMs = Date.now()),
                    this._modality.next("touch"),
                    (this._mostRecentTarget = Xi(s)));
              }),
              (this._options = { ...rU, ...o }),
              (this.modalityDetected = this._modality.pipe(qE(1))),
              (this.modalityChanged = this.modalityDetected.pipe(Wp())),
              n.isBrowser &&
                r.runOutsideAngular(() => {
                  i.addEventListener("keydown", this._onKeydown, Ji),
                    i.addEventListener("mousedown", this._onMousedown, Ji),
                    i.addEventListener("touchstart", this._onTouchstart, Ji);
                });
          }
          ngOnDestroy() {
            this._modality.complete(),
              this._platform.isBrowser &&
                (document.removeEventListener("keydown", this._onKeydown, Ji),
                document.removeEventListener(
                  "mousedown",
                  this._onMousedown,
                  Ji,
                ),
                document.removeEventListener(
                  "touchstart",
                  this._onTouchstart,
                  Ji,
                ));
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(Ar), D(W), D(ce), D(nU, 8));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      const sU = new E("cdk-focus-monitor-default-options"),
        Dl = yl({ passive: !0, capture: !0 });
      let aU = (() => {
        class e {
          constructor(n, r, i, o, s) {
            (this._ngZone = n),
              (this._platform = r),
              (this._inputModalityDetector = i),
              (this._origin = null),
              (this._windowFocused = !1),
              (this._originFromTouchInteraction = !1),
              (this._elementInfo = new Map()),
              (this._monitoredElementCount = 0),
              (this._rootNodeFocusListenerCount = new Map()),
              (this._windowFocusListener = () => {
                (this._windowFocused = !0),
                  (this._windowFocusTimeoutId = window.setTimeout(
                    () => (this._windowFocused = !1),
                  ));
              }),
              (this._stopInputModalityDetector = new Te()),
              (this._rootNodeFocusAndBlurListener = (a) => {
                for (let l = Xi(a); l; l = l.parentElement)
                  "focus" === a.type ? this._onFocus(a, l) : this._onBlur(a, l);
              }),
              (this._document = o),
              (this._detectionMode = s?.detectionMode || 0);
          }
          monitor(n, r = !1) {
            const i = ks(n);
            if (!this._platform.isBrowser || 1 !== i.nodeType) return A();
            const o =
                (function b$(e) {
                  if (
                    (function g$() {
                      if (null == gp) {
                        const e = typeof document < "u" ? document.head : null;
                        gp = !(!e || (!e.createShadowRoot && !e.attachShadow));
                      }
                      return gp;
                    })()
                  ) {
                    const t = e.getRootNode ? e.getRootNode() : null;
                    if (
                      typeof ShadowRoot < "u" &&
                      ShadowRoot &&
                      t instanceof ShadowRoot
                    )
                      return t;
                  }
                  return null;
                })(i) || this._getDocument(),
              s = this._elementInfo.get(i);
            if (s) return r && (s.checkChildren = !0), s.subject;
            const a = { checkChildren: r, subject: new Te(), rootNode: o };
            return (
              this._elementInfo.set(i, a),
              this._registerGlobalListeners(a),
              a.subject
            );
          }
          stopMonitoring(n) {
            const r = ks(n),
              i = this._elementInfo.get(r);
            i &&
              (i.subject.complete(),
              this._setClasses(r),
              this._elementInfo.delete(r),
              this._removeGlobalListeners(i));
          }
          focusVia(n, r, i) {
            const o = ks(n);
            o === this._getDocument().activeElement
              ? this._getClosestElementsInfo(o).forEach(([a, c]) =>
                  this._originChanged(a, r, c),
                )
              : (this._setOrigin(r),
                "function" == typeof o.focus && o.focus(i));
          }
          ngOnDestroy() {
            this._elementInfo.forEach((n, r) => this.stopMonitoring(r));
          }
          _getDocument() {
            return this._document || document;
          }
          _getWindow() {
            return this._getDocument().defaultView || window;
          }
          _getFocusOrigin(n) {
            return this._origin
              ? this._originFromTouchInteraction
                ? this._shouldBeAttributedToTouch(n)
                  ? "touch"
                  : "program"
                : this._origin
              : this._windowFocused && this._lastFocusOrigin
              ? this._lastFocusOrigin
              : n && this._isLastInteractionFromInputLabel(n)
              ? "mouse"
              : "program";
          }
          _shouldBeAttributedToTouch(n) {
            return (
              1 === this._detectionMode ||
              !!n?.contains(this._inputModalityDetector._mostRecentTarget)
            );
          }
          _setClasses(n, r) {
            n.classList.toggle("cdk-focused", !!r),
              n.classList.toggle("cdk-touch-focused", "touch" === r),
              n.classList.toggle("cdk-keyboard-focused", "keyboard" === r),
              n.classList.toggle("cdk-mouse-focused", "mouse" === r),
              n.classList.toggle("cdk-program-focused", "program" === r);
          }
          _setOrigin(n, r = !1) {
            this._ngZone.runOutsideAngular(() => {
              (this._origin = n),
                (this._originFromTouchInteraction = "touch" === n && r),
                0 === this._detectionMode &&
                  (clearTimeout(this._originTimeoutId),
                  (this._originTimeoutId = setTimeout(
                    () => (this._origin = null),
                    this._originFromTouchInteraction ? 650 : 1,
                  )));
            });
          }
          _onFocus(n, r) {
            const i = this._elementInfo.get(r),
              o = Xi(n);
            !i ||
              (!i.checkChildren && r !== o) ||
              this._originChanged(r, this._getFocusOrigin(o), i);
          }
          _onBlur(n, r) {
            const i = this._elementInfo.get(r);
            !i ||
              (i.checkChildren &&
                n.relatedTarget instanceof Node &&
                r.contains(n.relatedTarget)) ||
              (this._setClasses(r), this._emitOrigin(i, null));
          }
          _emitOrigin(n, r) {
            n.subject.observers.length &&
              this._ngZone.run(() => n.subject.next(r));
          }
          _registerGlobalListeners(n) {
            if (!this._platform.isBrowser) return;
            const r = n.rootNode,
              i = this._rootNodeFocusListenerCount.get(r) || 0;
            i ||
              this._ngZone.runOutsideAngular(() => {
                r.addEventListener(
                  "focus",
                  this._rootNodeFocusAndBlurListener,
                  Dl,
                ),
                  r.addEventListener(
                    "blur",
                    this._rootNodeFocusAndBlurListener,
                    Dl,
                  );
              }),
              this._rootNodeFocusListenerCount.set(r, i + 1),
              1 == ++this._monitoredElementCount &&
                (this._ngZone.runOutsideAngular(() => {
                  this._getWindow().addEventListener(
                    "focus",
                    this._windowFocusListener,
                  );
                }),
                this._inputModalityDetector.modalityDetected
                  .pipe(Gh(this._stopInputModalityDetector))
                  .subscribe((o) => {
                    this._setOrigin(o, !0);
                  }));
          }
          _removeGlobalListeners(n) {
            const r = n.rootNode;
            if (this._rootNodeFocusListenerCount.has(r)) {
              const i = this._rootNodeFocusListenerCount.get(r);
              i > 1
                ? this._rootNodeFocusListenerCount.set(r, i - 1)
                : (r.removeEventListener(
                    "focus",
                    this._rootNodeFocusAndBlurListener,
                    Dl,
                  ),
                  r.removeEventListener(
                    "blur",
                    this._rootNodeFocusAndBlurListener,
                    Dl,
                  ),
                  this._rootNodeFocusListenerCount.delete(r));
            }
            --this._monitoredElementCount ||
              (this._getWindow().removeEventListener(
                "focus",
                this._windowFocusListener,
              ),
              this._stopInputModalityDetector.next(),
              clearTimeout(this._windowFocusTimeoutId),
              clearTimeout(this._originTimeoutId));
          }
          _originChanged(n, r, i) {
            this._setClasses(n, r),
              this._emitOrigin(i, r),
              (this._lastFocusOrigin = r);
          }
          _getClosestElementsInfo(n) {
            const r = [];
            return (
              this._elementInfo.forEach((i, o) => {
                (o === n || (i.checkChildren && o.contains(n))) &&
                  r.push([o, i]);
              }),
              r
            );
          }
          _isLastInteractionFromInputLabel(n) {
            const { _mostRecentTarget: r, mostRecentModality: i } =
              this._inputModalityDetector;
            if (
              "mouse" !== i ||
              !r ||
              r === n ||
              ("INPUT" !== n.nodeName && "TEXTAREA" !== n.nodeName) ||
              n.disabled
            )
              return !1;
            const o = n.labels;
            if (o)
              for (let s = 0; s < o.length; s++)
                if (o[s].contains(r)) return !0;
            return !1;
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(W), D(Ar), D(iU), D(ce, 8), D(sU, 8));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      const tC = "cdk-high-contrast-black-on-white",
        nC = "cdk-high-contrast-white-on-black",
        bp = "cdk-high-contrast-active";
      let cU = (() => {
          class e {
            constructor(n, r) {
              (this._platform = n),
                (this._document = r),
                (this._breakpointSubscription = C(G$)
                  .observe("(forced-colors: active)")
                  .subscribe(() => {
                    this._hasCheckedHighContrastMode &&
                      ((this._hasCheckedHighContrastMode = !1),
                      this._applyBodyHighContrastModeCssClasses());
                  }));
            }
            getHighContrastMode() {
              if (!this._platform.isBrowser) return 0;
              const n = this._document.createElement("div");
              (n.style.backgroundColor = "rgb(1,2,3)"),
                (n.style.position = "absolute"),
                this._document.body.appendChild(n);
              const r = this._document.defaultView || window,
                i = r && r.getComputedStyle ? r.getComputedStyle(n) : null,
                o = ((i && i.backgroundColor) || "").replace(/ /g, "");
              switch ((n.remove(), o)) {
                case "rgb(0,0,0)":
                case "rgb(45,50,54)":
                case "rgb(32,32,32)":
                  return 2;
                case "rgb(255,255,255)":
                case "rgb(255,250,239)":
                  return 1;
              }
              return 0;
            }
            ngOnDestroy() {
              this._breakpointSubscription.unsubscribe();
            }
            _applyBodyHighContrastModeCssClasses() {
              if (
                !this._hasCheckedHighContrastMode &&
                this._platform.isBrowser &&
                this._document.body
              ) {
                const n = this._document.body.classList;
                n.remove(bp, tC, nC), (this._hasCheckedHighContrastMode = !0);
                const r = this.getHighContrastMode();
                1 === r ? n.add(bp, tC) : 2 === r && n.add(bp, nC);
              }
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(D(Ar), D(ce));
              };
            }
            static {
              this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
            }
          }
          return e;
        })(),
        rC = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵmod = Be({ type: e });
            }
            static {
              this.ɵinj = Ne({});
            }
          }
          return e;
        })();
      const fU = new E("mat-sanity-checks", {
        providedIn: "root",
        factory: function dU() {
          return !0;
        },
      });
      let Pn = (() => {
        class e {
          constructor(n, r, i) {
            (this._sanityChecks = r),
              (this._document = i),
              (this._hasDoneGlobalChecks = !1),
              n._applyBodyHighContrastModeCssClasses(),
              this._hasDoneGlobalChecks || (this._hasDoneGlobalChecks = !0);
          }
          _checkIsEnabled(n) {
            return (
              !(function y$() {
                return (
                  (typeof __karma__ < "u" && !!__karma__) ||
                  (typeof jasmine < "u" && !!jasmine) ||
                  (typeof jest < "u" && !!jest) ||
                  (typeof Mocha < "u" && !!Mocha)
                );
              })() &&
              ("boolean" == typeof this._sanityChecks
                ? this._sanityChecks
                : !!this._sanityChecks[n])
            );
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(cU), D(fU, 8), D(ce));
            };
          }
          static {
            this.ɵmod = Be({ type: e });
          }
          static {
            this.ɵinj = Ne({ imports: [rC, rC] });
          }
        }
        return e;
      })();
      function hU(e) {
        return class extends e {
          get disabled() {
            return this._disabled;
          }
          set disabled(t) {
            this._disabled = Ps(t);
          }
          constructor(...t) {
            super(...t), (this._disabled = !1);
          }
        };
      }
      function sC(e, t) {
        return class extends e {
          get color() {
            return this._color;
          }
          set color(n) {
            const r = n || this.defaultColor;
            r !== this._color &&
              (this._color &&
                this._elementRef.nativeElement.classList.remove(
                  `mat-${this._color}`,
                ),
              r && this._elementRef.nativeElement.classList.add(`mat-${r}`),
              (this._color = r));
          }
          constructor(...n) {
            super(...n), (this.defaultColor = t), (this.color = t);
          }
        };
      }
      function pU(e) {
        return class extends e {
          get disableRipple() {
            return this._disableRipple;
          }
          set disableRipple(t) {
            this._disableRipple = Ps(t);
          }
          constructor(...t) {
            super(...t), (this._disableRipple = !1);
          }
        };
      }
      class gU {
        constructor(t, n, r, i = !1) {
          (this._renderer = t),
            (this.element = n),
            (this.config = r),
            (this._animationForciblyDisabledThroughCss = i),
            (this.state = 3);
        }
        fadeOut() {
          this._renderer.fadeOutRipple(this);
        }
      }
      const aC = yl({ passive: !0, capture: !0 });
      class bU {
        constructor() {
          (this._events = new Map()),
            (this._delegateEventHandler = (t) => {
              const n = Xi(t);
              n &&
                this._events.get(t.type)?.forEach((r, i) => {
                  (i === n || i.contains(n)) &&
                    r.forEach((o) => o.handleEvent(t));
                });
            });
        }
        addHandler(t, n, r, i) {
          const o = this._events.get(n);
          if (o) {
            const s = o.get(r);
            s ? s.add(i) : o.set(r, new Set([i]));
          } else
            this._events.set(n, new Map([[r, new Set([i])]])),
              t.runOutsideAngular(() => {
                document.addEventListener(n, this._delegateEventHandler, aC);
              });
        }
        removeHandler(t, n, r) {
          const i = this._events.get(t);
          if (!i) return;
          const o = i.get(n);
          o &&
            (o.delete(r),
            0 === o.size && i.delete(n),
            0 === i.size &&
              (this._events.delete(t),
              document.removeEventListener(t, this._delegateEventHandler, aC)));
        }
      }
      const cC = { enterDuration: 225, exitDuration: 150 },
        lC = yl({ passive: !0, capture: !0 }),
        uC = ["mousedown", "touchstart"],
        dC = ["mouseup", "mouseleave", "touchend", "touchcancel"];
      class wl {
        static {
          this._eventManager = new bU();
        }
        constructor(t, n, r, i) {
          (this._target = t),
            (this._ngZone = n),
            (this._platform = i),
            (this._isPointerDown = !1),
            (this._activeRipples = new Map()),
            (this._pointerUpEventsRegistered = !1),
            i.isBrowser && (this._containerElement = ks(r));
        }
        fadeInRipple(t, n, r = {}) {
          const i = (this._containerRect =
              this._containerRect ||
              this._containerElement.getBoundingClientRect()),
            o = { ...cC, ...r.animation };
          r.centered &&
            ((t = i.left + i.width / 2), (n = i.top + i.height / 2));
          const s =
              r.radius ||
              (function vU(e, t, n) {
                const r = Math.max(Math.abs(e - n.left), Math.abs(e - n.right)),
                  i = Math.max(Math.abs(t - n.top), Math.abs(t - n.bottom));
                return Math.sqrt(r * r + i * i);
              })(t, n, i),
            a = t - i.left,
            c = n - i.top,
            l = o.enterDuration,
            u = document.createElement("div");
          u.classList.add("mat-ripple-element"),
            (u.style.left = a - s + "px"),
            (u.style.top = c - s + "px"),
            (u.style.height = 2 * s + "px"),
            (u.style.width = 2 * s + "px"),
            null != r.color && (u.style.backgroundColor = r.color),
            (u.style.transitionDuration = `${l}ms`),
            this._containerElement.appendChild(u);
          const d = window.getComputedStyle(u),
            h = d.transitionDuration,
            p =
              "none" === d.transitionProperty ||
              "0s" === h ||
              "0s, 0s" === h ||
              (0 === i.width && 0 === i.height),
            m = new gU(this, u, r, p);
          (u.style.transform = "scale3d(1, 1, 1)"),
            (m.state = 0),
            r.persistent || (this._mostRecentTransientRipple = m);
          let g = null;
          return (
            !p &&
              (l || o.exitDuration) &&
              this._ngZone.runOutsideAngular(() => {
                const y = () => this._finishRippleTransition(m),
                  b = () => this._destroyRipple(m);
                u.addEventListener("transitionend", y),
                  u.addEventListener("transitioncancel", b),
                  (g = { onTransitionEnd: y, onTransitionCancel: b });
              }),
            this._activeRipples.set(m, g),
            (p || !l) && this._finishRippleTransition(m),
            m
          );
        }
        fadeOutRipple(t) {
          if (2 === t.state || 3 === t.state) return;
          const n = t.element,
            r = { ...cC, ...t.config.animation };
          (n.style.transitionDuration = `${r.exitDuration}ms`),
            (n.style.opacity = "0"),
            (t.state = 2),
            (t._animationForciblyDisabledThroughCss || !r.exitDuration) &&
              this._finishRippleTransition(t);
        }
        fadeOutAll() {
          this._getActiveRipples().forEach((t) => t.fadeOut());
        }
        fadeOutAllNonPersistent() {
          this._getActiveRipples().forEach((t) => {
            t.config.persistent || t.fadeOut();
          });
        }
        setupTriggerEvents(t) {
          const n = ks(t);
          !this._platform.isBrowser ||
            !n ||
            n === this._triggerElement ||
            (this._removeTriggerEvents(),
            (this._triggerElement = n),
            uC.forEach((r) => {
              wl._eventManager.addHandler(this._ngZone, r, n, this);
            }));
        }
        handleEvent(t) {
          "mousedown" === t.type
            ? this._onMousedown(t)
            : "touchstart" === t.type
            ? this._onTouchStart(t)
            : this._onPointerUp(),
            this._pointerUpEventsRegistered ||
              (this._ngZone.runOutsideAngular(() => {
                dC.forEach((n) => {
                  this._triggerElement.addEventListener(n, this, lC);
                });
              }),
              (this._pointerUpEventsRegistered = !0));
        }
        _finishRippleTransition(t) {
          0 === t.state
            ? this._startFadeOutTransition(t)
            : 2 === t.state && this._destroyRipple(t);
        }
        _startFadeOutTransition(t) {
          const n = t === this._mostRecentTransientRipple,
            { persistent: r } = t.config;
          (t.state = 1), !r && (!n || !this._isPointerDown) && t.fadeOut();
        }
        _destroyRipple(t) {
          const n = this._activeRipples.get(t) ?? null;
          this._activeRipples.delete(t),
            this._activeRipples.size || (this._containerRect = null),
            t === this._mostRecentTransientRipple &&
              (this._mostRecentTransientRipple = null),
            (t.state = 3),
            null !== n &&
              (t.element.removeEventListener(
                "transitionend",
                n.onTransitionEnd,
              ),
              t.element.removeEventListener(
                "transitioncancel",
                n.onTransitionCancel,
              )),
            t.element.remove();
        }
        _onMousedown(t) {
          const n = XE(t),
            r =
              this._lastTouchStartEvent &&
              Date.now() < this._lastTouchStartEvent + 800;
          !this._target.rippleDisabled &&
            !n &&
            !r &&
            ((this._isPointerDown = !0),
            this.fadeInRipple(t.clientX, t.clientY, this._target.rippleConfig));
        }
        _onTouchStart(t) {
          if (!this._target.rippleDisabled && !JE(t)) {
            (this._lastTouchStartEvent = Date.now()),
              (this._isPointerDown = !0);
            const n = t.changedTouches;
            if (n)
              for (let r = 0; r < n.length; r++)
                this.fadeInRipple(
                  n[r].clientX,
                  n[r].clientY,
                  this._target.rippleConfig,
                );
          }
        }
        _onPointerUp() {
          this._isPointerDown &&
            ((this._isPointerDown = !1),
            this._getActiveRipples().forEach((t) => {
              !t.config.persistent &&
                (1 === t.state ||
                  (t.config.terminateOnPointerUp && 0 === t.state)) &&
                t.fadeOut();
            }));
        }
        _getActiveRipples() {
          return Array.from(this._activeRipples.keys());
        }
        _removeTriggerEvents() {
          const t = this._triggerElement;
          t &&
            (uC.forEach((n) => wl._eventManager.removeHandler(n, t, this)),
            this._pointerUpEventsRegistered &&
              dC.forEach((n) => t.removeEventListener(n, this, lC)));
        }
      }
      const fC = new E("mat-ripple-global-options");
      let _U = (() => {
          class e {
            get disabled() {
              return this._disabled;
            }
            set disabled(n) {
              n && this.fadeOutAllNonPersistent(),
                (this._disabled = n),
                this._setupTriggerEventsIfEnabled();
            }
            get trigger() {
              return this._trigger || this._elementRef.nativeElement;
            }
            set trigger(n) {
              (this._trigger = n), this._setupTriggerEventsIfEnabled();
            }
            constructor(n, r, i, o, s) {
              (this._elementRef = n),
                (this._animationMode = s),
                (this.radius = 0),
                (this._disabled = !1),
                (this._isInitialized = !1),
                (this._globalOptions = o || {}),
                (this._rippleRenderer = new wl(this, r, n, i));
            }
            ngOnInit() {
              (this._isInitialized = !0), this._setupTriggerEventsIfEnabled();
            }
            ngOnDestroy() {
              this._rippleRenderer._removeTriggerEvents();
            }
            fadeOutAll() {
              this._rippleRenderer.fadeOutAll();
            }
            fadeOutAllNonPersistent() {
              this._rippleRenderer.fadeOutAllNonPersistent();
            }
            get rippleConfig() {
              return {
                centered: this.centered,
                radius: this.radius,
                color: this.color,
                animation: {
                  ...this._globalOptions.animation,
                  ...("NoopAnimations" === this._animationMode
                    ? { enterDuration: 0, exitDuration: 0 }
                    : {}),
                  ...this.animation,
                },
                terminateOnPointerUp: this._globalOptions.terminateOnPointerUp,
              };
            }
            get rippleDisabled() {
              return this.disabled || !!this._globalOptions.disabled;
            }
            _setupTriggerEventsIfEnabled() {
              !this.disabled &&
                this._isInitialized &&
                this._rippleRenderer.setupTriggerEvents(this.trigger);
            }
            launch(n, r = 0, i) {
              return "number" == typeof n
                ? this._rippleRenderer.fadeInRipple(n, r, {
                    ...this.rippleConfig,
                    ...i,
                  })
                : this._rippleRenderer.fadeInRipple(0, 0, {
                    ...this.rippleConfig,
                    ...n,
                  });
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(x(gt), x(W), x(Ar), x(fC, 8), x(Oo, 8));
              };
            }
            static {
              this.ɵdir = re({
                type: e,
                selectors: [
                  ["", "mat-ripple", ""],
                  ["", "matRipple", ""],
                ],
                hostAttrs: [1, "mat-ripple"],
                hostVars: 2,
                hostBindings: function (r, i) {
                  2 & r && Gn("mat-ripple-unbounded", i.unbounded);
                },
                inputs: {
                  color: ["matRippleColor", "color"],
                  unbounded: ["matRippleUnbounded", "unbounded"],
                  centered: ["matRippleCentered", "centered"],
                  radius: ["matRippleRadius", "radius"],
                  animation: ["matRippleAnimation", "animation"],
                  disabled: ["matRippleDisabled", "disabled"],
                  trigger: ["matRippleTrigger", "trigger"],
                },
                exportAs: ["matRipple"],
              });
            }
          }
          return e;
        })(),
        DU = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵmod = Be({ type: e });
            }
            static {
              this.ɵinj = Ne({ imports: [Pn, Pn] });
            }
          }
          return e;
        })();
      const hC = { capture: !0 },
        pC = ["focus", "click", "mouseenter", "touchstart"],
        yp = "mat-ripple-loader-uninitialized",
        vp = "mat-ripple-loader-class-name",
        mC = "mat-ripple-loader-centered",
        El = "mat-ripple-loader-disabled";
      let wU = (() => {
        class e {
          constructor() {
            (this._document = C(ce, { optional: !0 })),
              (this._animationMode = C(Oo, { optional: !0 })),
              (this._globalRippleOptions = C(fC, { optional: !0 })),
              (this._platform = C(Ar)),
              (this._ngZone = C(W)),
              (this._hosts = new Map()),
              (this._onInteraction = (n) => {
                if (!(n.target instanceof HTMLElement)) return;
                const i = n.target.closest(`[${yp}]`);
                i && this._createRipple(i);
              }),
              this._ngZone.runOutsideAngular(() => {
                for (const n of pC)
                  this._document?.addEventListener(n, this._onInteraction, hC);
              });
          }
          ngOnDestroy() {
            const n = this._hosts.keys();
            for (const r of n) this.destroyRipple(r);
            for (const r of pC)
              this._document?.removeEventListener(r, this._onInteraction, hC);
          }
          configureRipple(n, r) {
            n.setAttribute(yp, ""),
              (r.className || !n.hasAttribute(vp)) &&
                n.setAttribute(vp, r.className || ""),
              r.centered && n.setAttribute(mC, ""),
              r.disabled && n.setAttribute(El, "");
          }
          getRipple(n) {
            return this._hosts.get(n) || this._createRipple(n);
          }
          setDisabled(n, r) {
            const i = this._hosts.get(n);
            i
              ? (i.disabled = r)
              : r
              ? n.setAttribute(El, "")
              : n.removeAttribute(El);
          }
          _createRipple(n) {
            if (!this._document) return;
            const r = this._hosts.get(n);
            if (r) return r;
            n.querySelector(".mat-ripple")?.remove();
            const i = this._document.createElement("span");
            i.classList.add("mat-ripple", n.getAttribute(vp)), n.append(i);
            const o = new _U(
              new gt(i),
              this._ngZone,
              this._platform,
              this._globalRippleOptions ? this._globalRippleOptions : void 0,
              this._animationMode ? this._animationMode : void 0,
            );
            return (
              (o._isInitialized = !0),
              (o.trigger = n),
              (o.centered = n.hasAttribute(mC)),
              (o.disabled = n.hasAttribute(El)),
              this.attachRipple(n, o),
              o
            );
          }
          attachRipple(n, r) {
            n.removeAttribute(yp), this._hosts.set(n, r);
          }
          destroyRipple(n) {
            const r = this._hosts.get(n);
            r && (r.ngOnDestroy(), this._hosts.delete(n));
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)();
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      const EU = ["*"],
        MU = [
          [
            ["", "mat-card-avatar", ""],
            ["", "matCardAvatar", ""],
          ],
          [
            ["mat-card-title"],
            ["mat-card-subtitle"],
            ["", "mat-card-title", ""],
            ["", "mat-card-subtitle", ""],
            ["", "matCardTitle", ""],
            ["", "matCardSubtitle", ""],
          ],
          "*",
        ],
        SU = [
          "[mat-card-avatar], [matCardAvatar]",
          "mat-card-title, mat-card-subtitle,\n      [mat-card-title], [mat-card-subtitle],\n      [matCardTitle], [matCardSubtitle]",
          "*",
        ],
        xU = new E("MAT_CARD_CONFIG");
      let gC = (() => {
          class e {
            constructor(n) {
              this.appearance = n?.appearance || "raised";
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(x(xU, 8));
              };
            }
            static {
              this.ɵcmp = bn({
                type: e,
                selectors: [["mat-card"]],
                hostAttrs: [1, "mat-mdc-card", "mdc-card"],
                hostVars: 4,
                hostBindings: function (r, i) {
                  2 & r &&
                    Gn("mat-mdc-card-outlined", "outlined" === i.appearance)(
                      "mdc-card--outlined",
                      "outlined" === i.appearance,
                    );
                },
                inputs: { appearance: "appearance" },
                exportAs: ["matCard"],
                ngContentSelectors: EU,
                decls: 1,
                vars: 0,
                template: function (r, i) {
                  1 & r && (xi(), At(0));
                },
                styles: [
                  '.mdc-card{display:flex;flex-direction:column;box-sizing:border-box}.mdc-card::after{position:absolute;box-sizing:border-box;width:100%;height:100%;top:0;left:0;border:1px solid rgba(0,0,0,0);border-radius:inherit;content:"";pointer-events:none;pointer-events:none}@media screen and (forced-colors: active){.mdc-card::after{border-color:CanvasText}}.mdc-card--outlined::after{border:none}.mdc-card__content{border-radius:inherit;height:100%}.mdc-card__media{position:relative;box-sizing:border-box;background-repeat:no-repeat;background-position:center;background-size:cover}.mdc-card__media::before{display:block;content:""}.mdc-card__media:first-child{border-top-left-radius:inherit;border-top-right-radius:inherit}.mdc-card__media:last-child{border-bottom-left-radius:inherit;border-bottom-right-radius:inherit}.mdc-card__media--square::before{margin-top:100%}.mdc-card__media--16-9::before{margin-top:56.25%}.mdc-card__media-content{position:absolute;top:0;right:0;bottom:0;left:0;box-sizing:border-box}.mdc-card__primary-action{display:flex;flex-direction:column;box-sizing:border-box;position:relative;outline:none;color:inherit;text-decoration:none;cursor:pointer;overflow:hidden}.mdc-card__primary-action:first-child{border-top-left-radius:inherit;border-top-right-radius:inherit}.mdc-card__primary-action:last-child{border-bottom-left-radius:inherit;border-bottom-right-radius:inherit}.mdc-card__actions{display:flex;flex-direction:row;align-items:center;box-sizing:border-box;min-height:52px;padding:8px}.mdc-card__actions--full-bleed{padding:0}.mdc-card__action-buttons,.mdc-card__action-icons{display:flex;flex-direction:row;align-items:center;box-sizing:border-box}.mdc-card__action-icons{color:rgba(0, 0, 0, 0.6);flex-grow:1;justify-content:flex-end}.mdc-card__action-buttons+.mdc-card__action-icons{margin-left:16px;margin-right:0}[dir=rtl] .mdc-card__action-buttons+.mdc-card__action-icons,.mdc-card__action-buttons+.mdc-card__action-icons[dir=rtl]{margin-left:0;margin-right:16px}.mdc-card__action{display:inline-flex;flex-direction:row;align-items:center;box-sizing:border-box;justify-content:center;cursor:pointer;user-select:none}.mdc-card__action:focus{outline:none}.mdc-card__action--button{margin-left:0;margin-right:8px;padding:0 8px}[dir=rtl] .mdc-card__action--button,.mdc-card__action--button[dir=rtl]{margin-left:8px;margin-right:0}.mdc-card__action--button:last-child{margin-left:0;margin-right:0}[dir=rtl] .mdc-card__action--button:last-child,.mdc-card__action--button:last-child[dir=rtl]{margin-left:0;margin-right:0}.mdc-card__actions--full-bleed .mdc-card__action--button{justify-content:space-between;width:100%;height:auto;max-height:none;margin:0;padding:8px 16px;text-align:left}[dir=rtl] .mdc-card__actions--full-bleed .mdc-card__action--button,.mdc-card__actions--full-bleed .mdc-card__action--button[dir=rtl]{text-align:right}.mdc-card__action--icon{margin:-6px 0;padding:12px}.mdc-card__action--icon:not(:disabled){color:rgba(0, 0, 0, 0.6)}.mat-mdc-card{border-radius:var(--mdc-elevated-card-container-shape);background-color:var(--mdc-elevated-card-container-color);border-width:0;border-style:solid;border-color:var(--mdc-elevated-card-container-color);box-shadow:var(--mdc-elevated-card-container-elevation);--mdc-elevated-card-container-shape:4px;--mdc-outlined-card-container-shape:4px;--mdc-outlined-card-outline-width:1px}.mat-mdc-card .mdc-card::after{border-radius:var(--mdc-elevated-card-container-shape)}.mat-mdc-card-outlined{border-width:var(--mdc-outlined-card-outline-width);border-style:solid;border-color:var(--mdc-outlined-card-outline-color);border-radius:var(--mdc-outlined-card-container-shape);background-color:var(--mdc-outlined-card-container-color);box-shadow:var(--mdc-outlined-card-container-elevation)}.mat-mdc-card-outlined .mdc-card::after{border-radius:var(--mdc-outlined-card-container-shape)}.mat-mdc-card-title{font-family:var(--mat-card-title-text-font);line-height:var(--mat-card-title-text-line-height);font-size:var(--mat-card-title-text-size);letter-spacing:var(--mat-card-title-text-tracking);font-weight:var(--mat-card-title-text-weight)}.mat-mdc-card-subtitle{color:var(--mat-card-subtitle-text-color);font-family:var(--mat-card-subtitle-text-font);line-height:var(--mat-card-subtitle-text-line-height);font-size:var(--mat-card-subtitle-text-size);letter-spacing:var(--mat-card-subtitle-text-tracking);font-weight:var(--mat-card-subtitle-text-weight)}.mat-mdc-card{position:relative}.mat-mdc-card-title,.mat-mdc-card-subtitle{display:block;margin:0}.mat-mdc-card-avatar~.mat-mdc-card-header-text .mat-mdc-card-title,.mat-mdc-card-avatar~.mat-mdc-card-header-text .mat-mdc-card-subtitle{padding:16px 16px 0}.mat-mdc-card-header{display:flex;padding:16px 16px 0}.mat-mdc-card-content{display:block;padding:0 16px}.mat-mdc-card-content:first-child{padding-top:16px}.mat-mdc-card-content:last-child{padding-bottom:16px}.mat-mdc-card-title-group{display:flex;justify-content:space-between;width:100%}.mat-mdc-card-avatar{height:40px;width:40px;border-radius:50%;flex-shrink:0;margin-bottom:16px;object-fit:cover}.mat-mdc-card-avatar~.mat-mdc-card-header-text .mat-mdc-card-subtitle,.mat-mdc-card-avatar~.mat-mdc-card-header-text .mat-mdc-card-title{line-height:normal}.mat-mdc-card-sm-image{width:80px;height:80px}.mat-mdc-card-md-image{width:112px;height:112px}.mat-mdc-card-lg-image{width:152px;height:152px}.mat-mdc-card-xl-image{width:240px;height:240px}.mat-mdc-card-subtitle~.mat-mdc-card-title,.mat-mdc-card-title~.mat-mdc-card-subtitle,.mat-mdc-card-header .mat-mdc-card-header-text .mat-mdc-card-title,.mat-mdc-card-header .mat-mdc-card-header-text .mat-mdc-card-subtitle,.mat-mdc-card-title-group .mat-mdc-card-title,.mat-mdc-card-title-group .mat-mdc-card-subtitle{padding-top:0}.mat-mdc-card-content>:last-child:not(.mat-mdc-card-footer){margin-bottom:0}.mat-mdc-card-actions-align-end{justify-content:flex-end}',
                ],
                encapsulation: 2,
                changeDetection: 0,
              });
            }
          }
          return e;
        })(),
        bC = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵdir = re({
                type: e,
                selectors: [
                  ["mat-card-title"],
                  ["", "mat-card-title", ""],
                  ["", "matCardTitle", ""],
                ],
                hostAttrs: [1, "mat-mdc-card-title"],
              });
            }
          }
          return e;
        })(),
        yC = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵdir = re({
                type: e,
                selectors: [["mat-card-content"]],
                hostAttrs: [1, "mat-mdc-card-content"],
              });
            }
          }
          return e;
        })(),
        vC = (() => {
          class e {
            constructor() {
              this.align = "start";
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵdir = re({
                type: e,
                selectors: [["mat-card-actions"]],
                hostAttrs: [1, "mat-mdc-card-actions", "mdc-card__actions"],
                hostVars: 2,
                hostBindings: function (r, i) {
                  2 & r &&
                    Gn("mat-mdc-card-actions-align-end", "end" === i.align);
                },
                inputs: { align: "align" },
                exportAs: ["matCardActions"],
              });
            }
          }
          return e;
        })(),
        _C = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵcmp = bn({
                type: e,
                selectors: [["mat-card-header"]],
                hostAttrs: [1, "mat-mdc-card-header"],
                ngContentSelectors: SU,
                decls: 4,
                vars: 0,
                consts: [[1, "mat-mdc-card-header-text"]],
                template: function (r, i) {
                  1 & r &&
                    (xi(MU), At(0), He(1, "div", 0), At(2, 1), ze(), At(3, 2));
                },
                encapsulation: 2,
                changeDetection: 0,
              });
            }
          }
          return e;
        })(),
        NU = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵmod = Be({ type: e });
            }
            static {
              this.ɵinj = Ne({ imports: [Pn, rh, Pn] });
            }
          }
          return e;
        })();
      const RU = ["mat-button", ""],
        OU = [
          [
            ["", 8, "material-icons", 3, "iconPositionEnd", ""],
            ["mat-icon", 3, "iconPositionEnd", ""],
            ["", "matButtonIcon", "", 3, "iconPositionEnd", ""],
          ],
          "*",
          [
            ["", "iconPositionEnd", "", 8, "material-icons"],
            ["mat-icon", "iconPositionEnd", ""],
            ["", "matButtonIcon", "", "iconPositionEnd", ""],
          ],
        ],
        PU = [
          ".material-icons:not([iconPositionEnd]), mat-icon:not([iconPositionEnd]), [matButtonIcon]:not([iconPositionEnd])",
          "*",
          ".material-icons[iconPositionEnd], mat-icon[iconPositionEnd], [matButtonIcon][iconPositionEnd]",
        ],
        kU = [
          {
            selector: "mat-button",
            mdcClasses: ["mdc-button", "mat-mdc-button"],
          },
          {
            selector: "mat-flat-button",
            mdcClasses: [
              "mdc-button",
              "mdc-button--unelevated",
              "mat-mdc-unelevated-button",
            ],
          },
          {
            selector: "mat-raised-button",
            mdcClasses: [
              "mdc-button",
              "mdc-button--raised",
              "mat-mdc-raised-button",
            ],
          },
          {
            selector: "mat-stroked-button",
            mdcClasses: [
              "mdc-button",
              "mdc-button--outlined",
              "mat-mdc-outlined-button",
            ],
          },
          { selector: "mat-fab", mdcClasses: ["mdc-fab", "mat-mdc-fab"] },
          {
            selector: "mat-mini-fab",
            mdcClasses: ["mdc-fab", "mdc-fab--mini", "mat-mdc-mini-fab"],
          },
          {
            selector: "mat-icon-button",
            mdcClasses: ["mdc-icon-button", "mat-mdc-icon-button"],
          },
        ],
        FU = sC(
          hU(
            pU(
              class {
                constructor(e) {
                  this._elementRef = e;
                }
              },
            ),
          ),
        );
      let LU = (() => {
          class e extends FU {
            get ripple() {
              return this._rippleLoader?.getRipple(
                this._elementRef.nativeElement,
              );
            }
            set ripple(n) {
              this._rippleLoader?.attachRipple(
                this._elementRef.nativeElement,
                n,
              );
            }
            get disableRipple() {
              return this._disableRipple;
            }
            set disableRipple(n) {
              (this._disableRipple = Ps(n)), this._updateRippleDisabled();
            }
            get disabled() {
              return this._disabled;
            }
            set disabled(n) {
              (this._disabled = Ps(n)), this._updateRippleDisabled();
            }
            constructor(n, r, i, o) {
              super(n),
                (this._platform = r),
                (this._ngZone = i),
                (this._animationMode = o),
                (this._focusMonitor = C(aU)),
                (this._rippleLoader = C(wU)),
                (this._isFab = !1),
                (this._disableRipple = !1),
                (this._disabled = !1),
                this._rippleLoader?.configureRipple(
                  this._elementRef.nativeElement,
                  { className: "mat-mdc-button-ripple" },
                );
              const s = n.nativeElement.classList;
              for (const a of kU)
                this._hasHostAttributes(a.selector) &&
                  a.mdcClasses.forEach((c) => {
                    s.add(c);
                  });
            }
            ngAfterViewInit() {
              this._focusMonitor.monitor(this._elementRef, !0);
            }
            ngOnDestroy() {
              this._focusMonitor.stopMonitoring(this._elementRef),
                this._rippleLoader?.destroyRipple(
                  this._elementRef.nativeElement,
                );
            }
            focus(n = "program", r) {
              n
                ? this._focusMonitor.focusVia(
                    this._elementRef.nativeElement,
                    n,
                    r,
                  )
                : this._elementRef.nativeElement.focus(r);
            }
            _hasHostAttributes(...n) {
              return n.some((r) =>
                this._elementRef.nativeElement.hasAttribute(r),
              );
            }
            _updateRippleDisabled() {
              this._rippleLoader?.setDisabled(
                this._elementRef.nativeElement,
                this.disableRipple || this.disabled,
              );
            }
            static {
              this.ɵfac = function (r) {
                Id();
              };
            }
            static {
              this.ɵdir = re({ type: e, features: [Uo] });
            }
          }
          return e;
        })(),
        BU = (() => {
          class e extends LU {
            constructor(n, r, i, o) {
              super(n, r, i, o);
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(x(gt), x(Ar), x(W), x(Oo, 8));
              };
            }
            static {
              this.ɵcmp = bn({
                type: e,
                selectors: [
                  ["button", "mat-button", ""],
                  ["button", "mat-raised-button", ""],
                  ["button", "mat-flat-button", ""],
                  ["button", "mat-stroked-button", ""],
                ],
                hostVars: 7,
                hostBindings: function (r, i) {
                  2 & r &&
                    (zo("disabled", i.disabled || null),
                    Gn(
                      "_mat-animation-noopable",
                      "NoopAnimations" === i._animationMode,
                    )("mat-unthemed", !i.color)("mat-mdc-button-base", !0));
                },
                inputs: {
                  disabled: "disabled",
                  disableRipple: "disableRipple",
                  color: "color",
                },
                exportAs: ["matButton"],
                features: [Uo],
                attrs: RU,
                ngContentSelectors: PU,
                decls: 7,
                vars: 4,
                consts: [
                  [1, "mat-mdc-button-persistent-ripple"],
                  [1, "mdc-button__label"],
                  [1, "mat-mdc-focus-indicator"],
                  [1, "mat-mdc-button-touch-target"],
                ],
                template: function (r, i) {
                  1 & r &&
                    (xi(OU),
                    gr(0, "span", 0),
                    At(1),
                    He(2, "span", 1),
                    At(3, 1),
                    ze(),
                    At(4, 2),
                    gr(5, "span", 2)(6, "span", 3)),
                    2 & r &&
                      Gn("mdc-button__ripple", !i._isFab)(
                        "mdc-fab__ripple",
                        i._isFab,
                      );
                },
                styles: [
                  '.mdc-touch-target-wrapper{display:inline}.mdc-elevation-overlay{position:absolute;border-radius:inherit;pointer-events:none;opacity:var(--mdc-elevation-overlay-opacity, 0);transition:opacity 280ms cubic-bezier(0.4, 0, 0.2, 1)}.mdc-button{position:relative;display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;min-width:64px;border:none;outline:none;line-height:inherit;user-select:none;-webkit-appearance:none;overflow:visible;vertical-align:middle;background:rgba(0,0,0,0)}.mdc-button .mdc-elevation-overlay{width:100%;height:100%;top:0;left:0}.mdc-button::-moz-focus-inner{padding:0;border:0}.mdc-button:active{outline:none}.mdc-button:hover{cursor:pointer}.mdc-button:disabled{cursor:default;pointer-events:none}.mdc-button[hidden]{display:none}.mdc-button .mdc-button__icon{margin-left:0;margin-right:8px;display:inline-block;position:relative;vertical-align:top}[dir=rtl] .mdc-button .mdc-button__icon,.mdc-button .mdc-button__icon[dir=rtl]{margin-left:8px;margin-right:0}.mdc-button .mdc-button__progress-indicator{font-size:0;position:absolute;transform:translate(-50%, -50%);top:50%;left:50%;line-height:initial}.mdc-button .mdc-button__label{position:relative}.mdc-button .mdc-button__focus-ring{pointer-events:none;border:2px solid rgba(0,0,0,0);border-radius:6px;box-sizing:content-box;position:absolute;top:50%;left:50%;transform:translate(-50%, -50%);height:calc(\n      100% + 4px\n    );width:calc(\n      100% + 4px\n    );display:none}@media screen and (forced-colors: active){.mdc-button .mdc-button__focus-ring{border-color:CanvasText}}.mdc-button .mdc-button__focus-ring::after{content:"";border:2px solid rgba(0,0,0,0);border-radius:8px;display:block;position:absolute;top:50%;left:50%;transform:translate(-50%, -50%);height:calc(100% + 4px);width:calc(100% + 4px)}@media screen and (forced-colors: active){.mdc-button .mdc-button__focus-ring::after{border-color:CanvasText}}@media screen and (forced-colors: active){.mdc-button.mdc-ripple-upgraded--background-focused .mdc-button__focus-ring,.mdc-button:not(.mdc-ripple-upgraded):focus .mdc-button__focus-ring{display:block}}.mdc-button .mdc-button__touch{position:absolute;top:50%;height:48px;left:0;right:0;transform:translateY(-50%)}.mdc-button__label+.mdc-button__icon{margin-left:8px;margin-right:0}[dir=rtl] .mdc-button__label+.mdc-button__icon,.mdc-button__label+.mdc-button__icon[dir=rtl]{margin-left:0;margin-right:8px}svg.mdc-button__icon{fill:currentColor}.mdc-button--touch{margin-top:6px;margin-bottom:6px}.mdc-button{padding:0 8px 0 8px}.mdc-button--unelevated{transition:box-shadow 280ms cubic-bezier(0.4, 0, 0.2, 1);padding:0 16px 0 16px}.mdc-button--unelevated.mdc-button--icon-trailing{padding:0 12px 0 16px}.mdc-button--unelevated.mdc-button--icon-leading{padding:0 16px 0 12px}.mdc-button--raised{transition:box-shadow 280ms cubic-bezier(0.4, 0, 0.2, 1);padding:0 16px 0 16px}.mdc-button--raised.mdc-button--icon-trailing{padding:0 12px 0 16px}.mdc-button--raised.mdc-button--icon-leading{padding:0 16px 0 12px}.mdc-button--outlined{border-style:solid;transition:border 280ms cubic-bezier(0.4, 0, 0.2, 1)}.mdc-button--outlined .mdc-button__ripple{border-style:solid;border-color:rgba(0,0,0,0)}.mat-mdc-button{height:var(--mdc-text-button-container-height, 36px);border-radius:var(--mdc-text-button-container-shape, var(--mdc-shape-small, 4px))}.mat-mdc-button:not(:disabled){color:var(--mdc-text-button-label-text-color, inherit)}.mat-mdc-button:disabled{color:var(--mdc-text-button-disabled-label-text-color, rgba(0, 0, 0, 0.38))}.mat-mdc-button .mdc-button__ripple{border-radius:var(--mdc-text-button-container-shape, var(--mdc-shape-small, 4px))}.mat-mdc-unelevated-button{height:var(--mdc-filled-button-container-height, 36px);border-radius:var(--mdc-filled-button-container-shape, var(--mdc-shape-small, 4px))}.mat-mdc-unelevated-button:not(:disabled){background-color:var(--mdc-filled-button-container-color, transparent)}.mat-mdc-unelevated-button:disabled{background-color:var(--mdc-filled-button-disabled-container-color, rgba(0, 0, 0, 0.12))}.mat-mdc-unelevated-button:not(:disabled){color:var(--mdc-filled-button-label-text-color, inherit)}.mat-mdc-unelevated-button:disabled{color:var(--mdc-filled-button-disabled-label-text-color, rgba(0, 0, 0, 0.38))}.mat-mdc-unelevated-button .mdc-button__ripple{border-radius:var(--mdc-filled-button-container-shape, var(--mdc-shape-small, 4px))}.mat-mdc-raised-button{height:var(--mdc-protected-button-container-height, 36px);border-radius:var(--mdc-protected-button-container-shape, var(--mdc-shape-small, 4px));box-shadow:var(--mdc-protected-button-container-elevation, 0px 3px 1px -2px rgba(0, 0, 0, 0.2), 0px 2px 2px 0px rgba(0, 0, 0, 0.14), 0px 1px 5px 0px rgba(0, 0, 0, 0.12))}.mat-mdc-raised-button:not(:disabled){background-color:var(--mdc-protected-button-container-color, transparent)}.mat-mdc-raised-button:disabled{background-color:var(--mdc-protected-button-disabled-container-color, rgba(0, 0, 0, 0.12))}.mat-mdc-raised-button:not(:disabled){color:var(--mdc-protected-button-label-text-color, inherit)}.mat-mdc-raised-button:disabled{color:var(--mdc-protected-button-disabled-label-text-color, rgba(0, 0, 0, 0.38))}.mat-mdc-raised-button .mdc-button__ripple{border-radius:var(--mdc-protected-button-container-shape, var(--mdc-shape-small, 4px))}.mat-mdc-raised-button.mdc-ripple-upgraded--background-focused,.mat-mdc-raised-button:not(.mdc-ripple-upgraded):focus{box-shadow:var(--mdc-protected-button-focus-container-elevation, 0px 2px 4px -1px rgba(0, 0, 0, 0.2), 0px 4px 5px 0px rgba(0, 0, 0, 0.14), 0px 1px 10px 0px rgba(0, 0, 0, 0.12))}.mat-mdc-raised-button:hover{box-shadow:var(--mdc-protected-button-hover-container-elevation, 0px 2px 4px -1px rgba(0, 0, 0, 0.2), 0px 4px 5px 0px rgba(0, 0, 0, 0.14), 0px 1px 10px 0px rgba(0, 0, 0, 0.12))}.mat-mdc-raised-button:not(:disabled):active{box-shadow:var(--mdc-protected-button-pressed-container-elevation, 0px 5px 5px -3px rgba(0, 0, 0, 0.2), 0px 8px 10px 1px rgba(0, 0, 0, 0.14), 0px 3px 14px 2px rgba(0, 0, 0, 0.12))}.mat-mdc-raised-button:disabled{box-shadow:var(--mdc-protected-button-disabled-container-elevation, 0px 0px 0px 0px rgba(0, 0, 0, 0.2), 0px 0px 0px 0px rgba(0, 0, 0, 0.14), 0px 0px 0px 0px rgba(0, 0, 0, 0.12))}.mat-mdc-outlined-button{height:var(--mdc-outlined-button-container-height, 36px);border-radius:var(--mdc-outlined-button-container-shape, var(--mdc-shape-small, 4px));padding:0 15px 0 15px;border-width:var(--mdc-outlined-button-outline-width, 1px)}.mat-mdc-outlined-button:not(:disabled){color:var(--mdc-outlined-button-label-text-color, inherit)}.mat-mdc-outlined-button:disabled{color:var(--mdc-outlined-button-disabled-label-text-color, rgba(0, 0, 0, 0.38))}.mat-mdc-outlined-button .mdc-button__ripple{border-radius:var(--mdc-outlined-button-container-shape, var(--mdc-shape-small, 4px))}.mat-mdc-outlined-button:not(:disabled){border-color:var(--mdc-outlined-button-outline-color, rgba(0, 0, 0, 0.12))}.mat-mdc-outlined-button:disabled{border-color:var(--mdc-outlined-button-disabled-outline-color, rgba(0, 0, 0, 0.12))}.mat-mdc-outlined-button.mdc-button--icon-trailing{padding:0 11px 0 15px}.mat-mdc-outlined-button.mdc-button--icon-leading{padding:0 15px 0 11px}.mat-mdc-outlined-button .mdc-button__ripple{top:-1px;left:-1px;bottom:-1px;right:-1px;border-width:var(--mdc-outlined-button-outline-width, 1px)}.mat-mdc-outlined-button .mdc-button__touch{left:calc(-1 * var(--mdc-outlined-button-outline-width, 1px));width:calc(100% + 2 * var(--mdc-outlined-button-outline-width, 1px))}.mat-mdc-button,.mat-mdc-unelevated-button,.mat-mdc-raised-button,.mat-mdc-outlined-button{-webkit-tap-highlight-color:rgba(0,0,0,0)}.mat-mdc-button .mat-mdc-button-ripple,.mat-mdc-button .mat-mdc-button-persistent-ripple,.mat-mdc-button .mat-mdc-button-persistent-ripple::before,.mat-mdc-unelevated-button .mat-mdc-button-ripple,.mat-mdc-unelevated-button .mat-mdc-button-persistent-ripple,.mat-mdc-unelevated-button .mat-mdc-button-persistent-ripple::before,.mat-mdc-raised-button .mat-mdc-button-ripple,.mat-mdc-raised-button .mat-mdc-button-persistent-ripple,.mat-mdc-raised-button .mat-mdc-button-persistent-ripple::before,.mat-mdc-outlined-button .mat-mdc-button-ripple,.mat-mdc-outlined-button .mat-mdc-button-persistent-ripple,.mat-mdc-outlined-button .mat-mdc-button-persistent-ripple::before{top:0;left:0;right:0;bottom:0;position:absolute;pointer-events:none;border-radius:inherit}.mat-mdc-button .mat-mdc-button-ripple,.mat-mdc-unelevated-button .mat-mdc-button-ripple,.mat-mdc-raised-button .mat-mdc-button-ripple,.mat-mdc-outlined-button .mat-mdc-button-ripple{overflow:hidden}.mat-mdc-button .mat-mdc-button-persistent-ripple::before,.mat-mdc-unelevated-button .mat-mdc-button-persistent-ripple::before,.mat-mdc-raised-button .mat-mdc-button-persistent-ripple::before,.mat-mdc-outlined-button .mat-mdc-button-persistent-ripple::before{content:"";opacity:0;background-color:var(--mat-mdc-button-persistent-ripple-color)}.mat-mdc-button .mat-ripple-element,.mat-mdc-unelevated-button .mat-ripple-element,.mat-mdc-raised-button .mat-ripple-element,.mat-mdc-outlined-button .mat-ripple-element{background-color:var(--mat-mdc-button-ripple-color)}.mat-mdc-button .mdc-button__label,.mat-mdc-unelevated-button .mdc-button__label,.mat-mdc-raised-button .mdc-button__label,.mat-mdc-outlined-button .mdc-button__label{z-index:1}.mat-mdc-button .mat-mdc-focus-indicator,.mat-mdc-unelevated-button .mat-mdc-focus-indicator,.mat-mdc-raised-button .mat-mdc-focus-indicator,.mat-mdc-outlined-button .mat-mdc-focus-indicator{top:0;left:0;right:0;bottom:0;position:absolute}.mat-mdc-button:focus .mat-mdc-focus-indicator::before,.mat-mdc-unelevated-button:focus .mat-mdc-focus-indicator::before,.mat-mdc-raised-button:focus .mat-mdc-focus-indicator::before,.mat-mdc-outlined-button:focus .mat-mdc-focus-indicator::before{content:""}.mat-mdc-button[disabled],.mat-mdc-unelevated-button[disabled],.mat-mdc-raised-button[disabled],.mat-mdc-outlined-button[disabled]{cursor:default;pointer-events:none}.mat-mdc-button .mat-mdc-button-touch-target,.mat-mdc-unelevated-button .mat-mdc-button-touch-target,.mat-mdc-raised-button .mat-mdc-button-touch-target,.mat-mdc-outlined-button .mat-mdc-button-touch-target{position:absolute;top:50%;height:48px;left:0;right:0;transform:translateY(-50%)}.mat-mdc-button._mat-animation-noopable,.mat-mdc-unelevated-button._mat-animation-noopable,.mat-mdc-raised-button._mat-animation-noopable,.mat-mdc-outlined-button._mat-animation-noopable{transition:none !important;animation:none !important}.mat-mdc-button>.mat-icon{margin-left:0;margin-right:8px;display:inline-block;position:relative;vertical-align:top;font-size:1.125rem;height:1.125rem;width:1.125rem}[dir=rtl] .mat-mdc-button>.mat-icon,.mat-mdc-button>.mat-icon[dir=rtl]{margin-left:8px;margin-right:0}.mat-mdc-button .mdc-button__label+.mat-icon{margin-left:8px;margin-right:0}[dir=rtl] .mat-mdc-button .mdc-button__label+.mat-icon,.mat-mdc-button .mdc-button__label+.mat-icon[dir=rtl]{margin-left:0;margin-right:8px}.mat-mdc-unelevated-button>.mat-icon,.mat-mdc-raised-button>.mat-icon,.mat-mdc-outlined-button>.mat-icon{margin-left:0;margin-right:8px;display:inline-block;position:relative;vertical-align:top;font-size:1.125rem;height:1.125rem;width:1.125rem;margin-left:-4px;margin-right:8px}[dir=rtl] .mat-mdc-unelevated-button>.mat-icon,[dir=rtl] .mat-mdc-raised-button>.mat-icon,[dir=rtl] .mat-mdc-outlined-button>.mat-icon,.mat-mdc-unelevated-button>.mat-icon[dir=rtl],.mat-mdc-raised-button>.mat-icon[dir=rtl],.mat-mdc-outlined-button>.mat-icon[dir=rtl]{margin-left:8px;margin-right:0}[dir=rtl] .mat-mdc-unelevated-button>.mat-icon,[dir=rtl] .mat-mdc-raised-button>.mat-icon,[dir=rtl] .mat-mdc-outlined-button>.mat-icon,.mat-mdc-unelevated-button>.mat-icon[dir=rtl],.mat-mdc-raised-button>.mat-icon[dir=rtl],.mat-mdc-outlined-button>.mat-icon[dir=rtl]{margin-left:8px;margin-right:-4px}.mat-mdc-unelevated-button .mdc-button__label+.mat-icon,.mat-mdc-raised-button .mdc-button__label+.mat-icon,.mat-mdc-outlined-button .mdc-button__label+.mat-icon{margin-left:8px;margin-right:-4px}[dir=rtl] .mat-mdc-unelevated-button .mdc-button__label+.mat-icon,[dir=rtl] .mat-mdc-raised-button .mdc-button__label+.mat-icon,[dir=rtl] .mat-mdc-outlined-button .mdc-button__label+.mat-icon,.mat-mdc-unelevated-button .mdc-button__label+.mat-icon[dir=rtl],.mat-mdc-raised-button .mdc-button__label+.mat-icon[dir=rtl],.mat-mdc-outlined-button .mdc-button__label+.mat-icon[dir=rtl]{margin-left:-4px;margin-right:8px}.mat-mdc-outlined-button .mat-mdc-button-ripple,.mat-mdc-outlined-button .mdc-button__ripple{top:-1px;left:-1px;bottom:-1px;right:-1px;border-width:-1px}.mat-mdc-unelevated-button .mat-mdc-focus-indicator::before,.mat-mdc-raised-button .mat-mdc-focus-indicator::before{margin:calc(calc(var(--mat-mdc-focus-indicator-border-width, 3px) + 2px) * -1)}.mat-mdc-outlined-button .mat-mdc-focus-indicator::before{margin:calc(calc(var(--mat-mdc-focus-indicator-border-width, 3px) + 3px) * -1)}',
                  ".cdk-high-contrast-active .mat-mdc-button:not(.mdc-button--outlined),.cdk-high-contrast-active .mat-mdc-unelevated-button:not(.mdc-button--outlined),.cdk-high-contrast-active .mat-mdc-raised-button:not(.mdc-button--outlined),.cdk-high-contrast-active .mat-mdc-outlined-button:not(.mdc-button--outlined),.cdk-high-contrast-active .mat-mdc-icon-button{outline:solid 1px}",
                ],
                encapsulation: 2,
                changeDetection: 0,
              });
            }
          }
          return e;
        })(),
        $U = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵmod = Be({ type: e });
            }
            static {
              this.ɵinj = Ne({ imports: [Pn, DU, Pn] });
            }
          }
          return e;
        })();
      const HU = ["*"];
      let Cl;
      function Ls(e) {
        return (
          (function zU() {
            if (void 0 === Cl && ((Cl = null), typeof window < "u")) {
              const e = window;
              void 0 !== e.trustedTypes &&
                (Cl = e.trustedTypes.createPolicy("angular#components", {
                  createHTML: (t) => t,
                }));
            }
            return Cl;
          })()?.createHTML(e) || e
        );
      }
      function DC(e) {
        return Error(`Unable to find icon with the name "${e}"`);
      }
      function wC(e) {
        return Error(
          `The URL provided to MatIconRegistry was not trusted as a resource URL via Angular's DomSanitizer. Attempted URL was "${e}".`,
        );
      }
      function EC(e) {
        return Error(
          `The literal provided to MatIconRegistry was not trusted as safe HTML by Angular's DomSanitizer. Attempted literal was "${e}".`,
        );
      }
      class Or {
        constructor(t, n, r) {
          (this.url = t), (this.svgText = n), (this.options = r);
        }
      }
      let Il = (() => {
        class e {
          constructor(n, r, i, o) {
            (this._httpClient = n),
              (this._sanitizer = r),
              (this._errorHandler = o),
              (this._svgIconConfigs = new Map()),
              (this._iconSetConfigs = new Map()),
              (this._cachedIconsByUrl = new Map()),
              (this._inProgressUrlFetches = new Map()),
              (this._fontCssClassesByAlias = new Map()),
              (this._resolvers = []),
              (this._defaultFontSetClass = [
                "material-icons",
                "mat-ligature-font",
              ]),
              (this._document = i);
          }
          addSvgIcon(n, r, i) {
            return this.addSvgIconInNamespace("", n, r, i);
          }
          addSvgIconLiteral(n, r, i) {
            return this.addSvgIconLiteralInNamespace("", n, r, i);
          }
          addSvgIconInNamespace(n, r, i, o) {
            return this._addSvgIconConfig(n, r, new Or(i, null, o));
          }
          addSvgIconResolver(n) {
            return this._resolvers.push(n), this;
          }
          addSvgIconLiteralInNamespace(n, r, i, o) {
            const s = this._sanitizer.sanitize(Fe.HTML, i);
            if (!s) throw EC(i);
            const a = Ls(s);
            return this._addSvgIconConfig(n, r, new Or("", a, o));
          }
          addSvgIconSet(n, r) {
            return this.addSvgIconSetInNamespace("", n, r);
          }
          addSvgIconSetLiteral(n, r) {
            return this.addSvgIconSetLiteralInNamespace("", n, r);
          }
          addSvgIconSetInNamespace(n, r, i) {
            return this._addSvgIconSetConfig(n, new Or(r, null, i));
          }
          addSvgIconSetLiteralInNamespace(n, r, i) {
            const o = this._sanitizer.sanitize(Fe.HTML, r);
            if (!o) throw EC(r);
            const s = Ls(o);
            return this._addSvgIconSetConfig(n, new Or("", s, i));
          }
          registerFontClassAlias(n, r = n) {
            return this._fontCssClassesByAlias.set(n, r), this;
          }
          classNameForFontAlias(n) {
            return this._fontCssClassesByAlias.get(n) || n;
          }
          setDefaultFontSetClass(...n) {
            return (this._defaultFontSetClass = n), this;
          }
          getDefaultFontSetClass() {
            return this._defaultFontSetClass;
          }
          getSvgIconFromUrl(n) {
            const r = this._sanitizer.sanitize(Fe.RESOURCE_URL, n);
            if (!r) throw wC(n);
            const i = this._cachedIconsByUrl.get(r);
            return i
              ? A(Ml(i))
              : this._loadSvgIconFromConfig(new Or(n, null)).pipe(
                  Ee((o) => this._cachedIconsByUrl.set(r, o)),
                  U((o) => Ml(o)),
                );
          }
          getNamedSvgIcon(n, r = "") {
            const i = CC(r, n);
            let o = this._svgIconConfigs.get(i);
            if (o) return this._getSvgFromConfig(o);
            if (((o = this._getIconConfigFromResolvers(r, n)), o))
              return this._svgIconConfigs.set(i, o), this._getSvgFromConfig(o);
            const s = this._iconSetConfigs.get(r);
            return s ? this._getSvgFromIconSetConfigs(n, s) : $i(DC(i));
          }
          ngOnDestroy() {
            (this._resolvers = []),
              this._svgIconConfigs.clear(),
              this._iconSetConfigs.clear(),
              this._cachedIconsByUrl.clear();
          }
          _getSvgFromConfig(n) {
            return n.svgText
              ? A(Ml(this._svgElementFromConfig(n)))
              : this._loadSvgIconFromConfig(n).pipe(U((r) => Ml(r)));
          }
          _getSvgFromIconSetConfigs(n, r) {
            const i = this._extractIconWithNameFromAnySet(n, r);
            return i
              ? A(i)
              : (function UU(...e) {
                  const t = Hp(e),
                    { args: n, keys: r } = Rw(e),
                    i = new pe((o) => {
                      const { length: s } = n;
                      if (!s) return void o.complete();
                      const a = new Array(s);
                      let c = s,
                        l = s;
                      for (let u = 0; u < s; u++) {
                        let d = !1;
                        ct(n[u]).subscribe(
                          be(
                            o,
                            (f) => {
                              d || ((d = !0), l--), (a[u] = f);
                            },
                            () => c--,
                            void 0,
                            () => {
                              (!c || !d) &&
                                (l || o.next(r ? Pw(r, a) : a), o.complete());
                            },
                          ),
                        );
                      }
                    });
                  return t ? i.pipe(Ow(t)) : i;
                })(
                  r
                    .filter((s) => !s.svgText)
                    .map((s) =>
                      this._loadSvgIconSetFromConfig(s).pipe(
                        Jn((a) => {
                          const l = `Loading icon set URL: ${this._sanitizer.sanitize(
                            Fe.RESOURCE_URL,
                            s.url,
                          )} failed: ${a.message}`;
                          return (
                            this._errorHandler.handleError(new Error(l)),
                            A(null)
                          );
                        }),
                      ),
                    ),
                ).pipe(
                  U(() => {
                    const s = this._extractIconWithNameFromAnySet(n, r);
                    if (!s) throw DC(n);
                    return s;
                  }),
                );
          }
          _extractIconWithNameFromAnySet(n, r) {
            for (let i = r.length - 1; i >= 0; i--) {
              const o = r[i];
              if (o.svgText && o.svgText.toString().indexOf(n) > -1) {
                const s = this._svgElementFromConfig(o),
                  a = this._extractSvgIconFromSet(s, n, o.options);
                if (a) return a;
              }
            }
            return null;
          }
          _loadSvgIconFromConfig(n) {
            return this._fetchIcon(n).pipe(
              Ee((r) => (n.svgText = r)),
              U(() => this._svgElementFromConfig(n)),
            );
          }
          _loadSvgIconSetFromConfig(n) {
            return n.svgText
              ? A(null)
              : this._fetchIcon(n).pipe(Ee((r) => (n.svgText = r)));
          }
          _extractSvgIconFromSet(n, r, i) {
            const o = n.querySelector(`[id="${r}"]`);
            if (!o) return null;
            const s = o.cloneNode(!0);
            if ((s.removeAttribute("id"), "svg" === s.nodeName.toLowerCase()))
              return this._setSvgAttributes(s, i);
            if ("symbol" === s.nodeName.toLowerCase())
              return this._setSvgAttributes(this._toSvgElement(s), i);
            const a = this._svgElementFromString(Ls("<svg></svg>"));
            return a.appendChild(s), this._setSvgAttributes(a, i);
          }
          _svgElementFromString(n) {
            const r = this._document.createElement("DIV");
            r.innerHTML = n;
            const i = r.querySelector("svg");
            if (!i) throw Error("<svg> tag not found");
            return i;
          }
          _toSvgElement(n) {
            const r = this._svgElementFromString(Ls("<svg></svg>")),
              i = n.attributes;
            for (let o = 0; o < i.length; o++) {
              const { name: s, value: a } = i[o];
              "id" !== s && r.setAttribute(s, a);
            }
            for (let o = 0; o < n.childNodes.length; o++)
              n.childNodes[o].nodeType === this._document.ELEMENT_NODE &&
                r.appendChild(n.childNodes[o].cloneNode(!0));
            return r;
          }
          _setSvgAttributes(n, r) {
            return (
              n.setAttribute("fit", ""),
              n.setAttribute("height", "100%"),
              n.setAttribute("width", "100%"),
              n.setAttribute("preserveAspectRatio", "xMidYMid meet"),
              n.setAttribute("focusable", "false"),
              r && r.viewBox && n.setAttribute("viewBox", r.viewBox),
              n
            );
          }
          _fetchIcon(n) {
            const { url: r, options: i } = n,
              o = i?.withCredentials ?? !1;
            if (!this._httpClient)
              throw (function qU() {
                return Error(
                  "Could not find HttpClient provider for use with Angular Material icons. Please include the HttpClientModule from @angular/common/http in your app imports.",
                );
              })();
            if (null == r) throw Error(`Cannot fetch icon from URL "${r}".`);
            const s = this._sanitizer.sanitize(Fe.RESOURCE_URL, r);
            if (!s) throw wC(r);
            const a = this._inProgressUrlFetches.get(s);
            if (a) return a;
            const c = this._httpClient
              .get(s, { responseType: "text", withCredentials: o })
              .pipe(
                U((l) => Ls(l)),
                ji(() => this._inProgressUrlFetches.delete(s)),
                $l(),
              );
            return this._inProgressUrlFetches.set(s, c), c;
          }
          _addSvgIconConfig(n, r, i) {
            return this._svgIconConfigs.set(CC(n, r), i), this;
          }
          _addSvgIconSetConfig(n, r) {
            const i = this._iconSetConfigs.get(n);
            return i ? i.push(r) : this._iconSetConfigs.set(n, [r]), this;
          }
          _svgElementFromConfig(n) {
            if (!n.svgElement) {
              const r = this._svgElementFromString(n.svgText);
              this._setSvgAttributes(r, n.options), (n.svgElement = r);
            }
            return n.svgElement;
          }
          _getIconConfigFromResolvers(n, r) {
            for (let i = 0; i < this._resolvers.length; i++) {
              const o = this._resolvers[i](r, n);
              if (o)
                return WU(o) ? new Or(o.url, null, o.options) : new Or(o, null);
            }
          }
          static {
            this.ɵfac = function (r) {
              return new (r || e)(D(Qc, 8), D(mh), D(ce, 8), D(xt));
            };
          }
          static {
            this.ɵprov = S({ token: e, factory: e.ɵfac, providedIn: "root" });
          }
        }
        return e;
      })();
      function Ml(e) {
        return e.cloneNode(!0);
      }
      function CC(e, t) {
        return e + ":" + t;
      }
      function WU(e) {
        return !(!e.url || !e.options);
      }
      const KU = sC(
          class {
            constructor(e) {
              this._elementRef = e;
            }
          },
        ),
        ZU = new E("MAT_ICON_DEFAULT_OPTIONS"),
        QU = new E("mat-icon-location", {
          providedIn: "root",
          factory: function YU() {
            const e = C(ce),
              t = e ? e.location : null;
            return { getPathname: () => (t ? t.pathname + t.search : "") };
          },
        }),
        IC = [
          "clip-path",
          "color-profile",
          "src",
          "cursor",
          "fill",
          "filter",
          "marker",
          "marker-start",
          "marker-mid",
          "marker-end",
          "mask",
          "stroke",
        ],
        XU = IC.map((e) => `[${e}]`).join(", "),
        JU = /^url\(['"]?#(.*?)['"]?\)$/;
      let eH = (() => {
          class e extends KU {
            get inline() {
              return this._inline;
            }
            set inline(n) {
              this._inline = Ps(n);
            }
            get svgIcon() {
              return this._svgIcon;
            }
            set svgIcon(n) {
              n !== this._svgIcon &&
                (n
                  ? this._updateSvgIcon(n)
                  : this._svgIcon && this._clearSvgElement(),
                (this._svgIcon = n));
            }
            get fontSet() {
              return this._fontSet;
            }
            set fontSet(n) {
              const r = this._cleanupFontValue(n);
              r !== this._fontSet &&
                ((this._fontSet = r), this._updateFontIconClasses());
            }
            get fontIcon() {
              return this._fontIcon;
            }
            set fontIcon(n) {
              const r = this._cleanupFontValue(n);
              r !== this._fontIcon &&
                ((this._fontIcon = r), this._updateFontIconClasses());
            }
            constructor(n, r, i, o, s, a) {
              super(n),
                (this._iconRegistry = r),
                (this._location = o),
                (this._errorHandler = s),
                (this._inline = !1),
                (this._previousFontSetClass = []),
                (this._currentIconFetch = je.EMPTY),
                a &&
                  (a.color && (this.color = this.defaultColor = a.color),
                  a.fontSet && (this.fontSet = a.fontSet)),
                i || n.nativeElement.setAttribute("aria-hidden", "true");
            }
            _splitIconName(n) {
              if (!n) return ["", ""];
              const r = n.split(":");
              switch (r.length) {
                case 1:
                  return ["", r[0]];
                case 2:
                  return r;
                default:
                  throw Error(`Invalid icon name: "${n}"`);
              }
            }
            ngOnInit() {
              this._updateFontIconClasses();
            }
            ngAfterViewChecked() {
              const n = this._elementsWithExternalReferences;
              if (n && n.size) {
                const r = this._location.getPathname();
                r !== this._previousPath &&
                  ((this._previousPath = r), this._prependPathToReferences(r));
              }
            }
            ngOnDestroy() {
              this._currentIconFetch.unsubscribe(),
                this._elementsWithExternalReferences &&
                  this._elementsWithExternalReferences.clear();
            }
            _usingFontIcon() {
              return !this.svgIcon;
            }
            _setSvgElement(n) {
              this._clearSvgElement();
              const r = this._location.getPathname();
              (this._previousPath = r),
                this._cacheChildrenWithExternalReferences(n),
                this._prependPathToReferences(r),
                this._elementRef.nativeElement.appendChild(n);
            }
            _clearSvgElement() {
              const n = this._elementRef.nativeElement;
              let r = n.childNodes.length;
              for (
                this._elementsWithExternalReferences &&
                this._elementsWithExternalReferences.clear();
                r--;

              ) {
                const i = n.childNodes[r];
                (1 !== i.nodeType || "svg" === i.nodeName.toLowerCase()) &&
                  i.remove();
              }
            }
            _updateFontIconClasses() {
              if (!this._usingFontIcon()) return;
              const n = this._elementRef.nativeElement,
                r = (
                  this.fontSet
                    ? this._iconRegistry
                        .classNameForFontAlias(this.fontSet)
                        .split(/ +/)
                    : this._iconRegistry.getDefaultFontSetClass()
                ).filter((i) => i.length > 0);
              this._previousFontSetClass.forEach((i) => n.classList.remove(i)),
                r.forEach((i) => n.classList.add(i)),
                (this._previousFontSetClass = r),
                this.fontIcon !== this._previousFontIconClass &&
                  !r.includes("mat-ligature-font") &&
                  (this._previousFontIconClass &&
                    n.classList.remove(this._previousFontIconClass),
                  this.fontIcon && n.classList.add(this.fontIcon),
                  (this._previousFontIconClass = this.fontIcon));
            }
            _cleanupFontValue(n) {
              return "string" == typeof n ? n.trim().split(" ")[0] : n;
            }
            _prependPathToReferences(n) {
              const r = this._elementsWithExternalReferences;
              r &&
                r.forEach((i, o) => {
                  i.forEach((s) => {
                    o.setAttribute(s.name, `url('${n}#${s.value}')`);
                  });
                });
            }
            _cacheChildrenWithExternalReferences(n) {
              const r = n.querySelectorAll(XU),
                i = (this._elementsWithExternalReferences =
                  this._elementsWithExternalReferences || new Map());
              for (let o = 0; o < r.length; o++)
                IC.forEach((s) => {
                  const a = r[o],
                    c = a.getAttribute(s),
                    l = c ? c.match(JU) : null;
                  if (l) {
                    let u = i.get(a);
                    u || ((u = []), i.set(a, u)),
                      u.push({ name: s, value: l[1] });
                  }
                });
            }
            _updateSvgIcon(n) {
              if (
                ((this._svgNamespace = null),
                (this._svgName = null),
                this._currentIconFetch.unsubscribe(),
                n)
              ) {
                const [r, i] = this._splitIconName(n);
                r && (this._svgNamespace = r),
                  i && (this._svgName = i),
                  (this._currentIconFetch = this._iconRegistry
                    .getNamedSvgIcon(i, r)
                    .pipe(Nn(1))
                    .subscribe(
                      (o) => this._setSvgElement(o),
                      (o) => {
                        this._errorHandler.handleError(
                          new Error(
                            `Error retrieving icon ${r}:${i}! ${o.message}`,
                          ),
                        );
                      },
                    ));
              }
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(
                  x(gt),
                  x(Il),
                  (function Do(e) {
                    return (function hS(e, t) {
                      if ("class" === t) return e.classes;
                      if ("style" === t) return e.styles;
                      const n = e.attrs;
                      if (n) {
                        const r = n.length;
                        let i = 0;
                        for (; i < r; ) {
                          const o = n[i];
                          if (om(o)) break;
                          if (0 === o) i += 2;
                          else if ("number" == typeof o)
                            for (i++; i < r && "string" == typeof n[i]; ) i++;
                          else {
                            if (o === t) return n[i + 1];
                            i += 2;
                          }
                        }
                      }
                      return null;
                    })(ke(), e);
                  })("aria-hidden"),
                  x(QU),
                  x(xt),
                  x(ZU, 8),
                );
              };
            }
            static {
              this.ɵcmp = bn({
                type: e,
                selectors: [["mat-icon"]],
                hostAttrs: ["role", "img", 1, "mat-icon", "notranslate"],
                hostVars: 8,
                hostBindings: function (r, i) {
                  2 & r &&
                    (zo(
                      "data-mat-icon-type",
                      i._usingFontIcon() ? "font" : "svg",
                    )("data-mat-icon-name", i._svgName || i.fontIcon)(
                      "data-mat-icon-namespace",
                      i._svgNamespace || i.fontSet,
                    )("fontIcon", i._usingFontIcon() ? i.fontIcon : null),
                    Gn("mat-icon-inline", i.inline)(
                      "mat-icon-no-color",
                      "primary" !== i.color &&
                        "accent" !== i.color &&
                        "warn" !== i.color,
                    ));
                },
                inputs: {
                  color: "color",
                  inline: "inline",
                  svgIcon: "svgIcon",
                  fontSet: "fontSet",
                  fontIcon: "fontIcon",
                },
                exportAs: ["matIcon"],
                features: [Uo],
                ngContentSelectors: HU,
                decls: 1,
                vars: 0,
                template: function (r, i) {
                  1 & r && (xi(), At(0));
                },
                styles: [
                  "mat-icon,mat-icon.mat-primary,mat-icon.mat-accent,mat-icon.mat-warn{color:var(--mat-icon-color)}.mat-icon{-webkit-user-select:none;user-select:none;background-repeat:no-repeat;display:inline-block;fill:currentColor;height:24px;width:24px;overflow:hidden}.mat-icon.mat-icon-inline{font-size:inherit;height:inherit;line-height:inherit;width:inherit}.mat-icon.mat-ligature-font[fontIcon]::before{content:attr(fontIcon)}[dir=rtl] .mat-icon-rtl-mirror{transform:scale(-1, 1)}.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-form-field-prefix .mat-icon,.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-form-field-suffix .mat-icon{display:block}.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-form-field-prefix .mat-icon-button .mat-icon,.mat-form-field:not(.mat-form-field-appearance-legacy) .mat-form-field-suffix .mat-icon-button .mat-icon{margin:auto}",
                ],
                encapsulation: 2,
                changeDetection: 0,
              });
            }
          }
          return e;
        })(),
        tH = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵmod = Be({ type: e });
            }
            static {
              this.ɵinj = Ne({ imports: [Pn, Pn] });
            }
          }
          return e;
        })();
      function nH(e, t) {
        1 & e && (He(0, "mat-icon"), Cn(1, "sync"), ze());
      }
      function rH(e, t) {
        1 & e && (He(0, "mat-icon"), Cn(1, "check_circle"), ze());
      }
      function iH(e, t) {
        1 & e && (He(0, "mat-icon"), Cn(1, "error"), ze());
      }
      let oH = (() => {
          class e {
            constructor(n) {
              (this.apiService = n),
                (this.backendStatus = "loading"),
                (this.statusMessage =
                  "Verificando conexi\xf3n con el backend...");
            }
            ngOnInit() {
              this.checkBackendStatus();
            }
            checkBackendStatus() {
              (this.backendStatus = "loading"),
                (this.statusMessage =
                  "Verificando conexi\xf3n con el backend..."),
                this.apiService.checkBackendStatus().subscribe({
                  next: (n) => {
                    (this.backendStatus = "connected"),
                      (this.statusMessage =
                        "Conexi\xf3n establecida con el backend"),
                      console.log("Backend conectado:", n);
                  },
                  error: (n) => {
                    (this.backendStatus = "error"),
                      (this.statusMessage =
                        "No se pudo conectar con el backend"),
                      console.error("Error de conexi\xf3n:", n);
                  },
                });
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)(x(p$));
              };
            }
            static {
              this.ɵcmp = bn({
                type: e,
                selectors: [["app-status-checker"]],
                decls: 15,
                vars: 5,
                consts: [
                  [1, "status-container"],
                  [1, "status-indicator", 3, "ngClass"],
                  [4, "ngIf"],
                  ["mat-raised-button", "", "color", "primary", 3, "click"],
                ],
                template: function (r, i) {
                  1 & r &&
                    (He(0, "div", 0)(1, "mat-card")(2, "mat-card-header")(
                      3,
                      "mat-card-title",
                    ),
                    Cn(4, "Estado del Servidor"),
                    ze()(),
                    He(5, "mat-card-content")(6, "div", 1),
                    ec(7, nH, 2, 0, "mat-icon", 2),
                    ec(8, rH, 2, 0, "mat-icon", 2),
                    ec(9, iH, 2, 0, "mat-icon", 2),
                    He(10, "p"),
                    Cn(11),
                    ze()()(),
                    He(12, "mat-card-actions")(13, "button", 3),
                    nc("click", function () {
                      return i.checkBackendStatus();
                    }),
                    Cn(14, " Verificar Conexi\xf3n "),
                    ze()()()()),
                    2 & r &&
                      (gi(6),
                      Si("ngClass", i.backendStatus),
                      gi(1),
                      Si("ngIf", "loading" === i.backendStatus),
                      gi(1),
                      Si("ngIf", "connected" === i.backendStatus),
                      gi(1),
                      Si("ngIf", "error" === i.backendStatus),
                      gi(2),
                      Yd(i.statusMessage));
                },
                dependencies: [tD, iD, gC, vC, yC, _C, bC, BU, eH],
                styles: [
                  ".status-container[_ngcontent-%COMP%]{padding:20px;max-width:500px;margin:0 auto}.status-indicator[_ngcontent-%COMP%]{display:flex;flex-direction:column;align-items:center;padding:20px 0}.status-indicator[_ngcontent-%COMP%]   mat-icon[_ngcontent-%COMP%]{font-size:48px;height:48px;width:48px;margin-bottom:10px}.status-indicator[_ngcontent-%COMP%]   p[_ngcontent-%COMP%]{font-size:16px;text-align:center}.status-indicator.loading[_ngcontent-%COMP%]{color:#1976d2}.status-indicator.loading[_ngcontent-%COMP%]   mat-icon[_ngcontent-%COMP%]{animation:_ngcontent-%COMP%_spin 1.5s linear infinite}.status-indicator.connected[_ngcontent-%COMP%]{color:#4caf50}.status-indicator.error[_ngcontent-%COMP%]{color:#f44336}@keyframes _ngcontent-%COMP%_spin{to{transform:rotate(360deg)}}",
                ],
              });
            }
          }
          return e;
        })(),
        sH = (() => {
          class e {
            constructor() {
              this.title = "frontend";
            }
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵcmp = bn({
                type: e,
                selectors: [["app-root"]],
                decls: 9,
                vars: 0,
                consts: [
                  [1, "container"],
                  [1, "app-header"],
                ],
                template: function (r, i) {
                  1 & r &&
                    (He(0, "div", 0)(1, "header", 1)(2, "h1"),
                    Cn(3, "TechStore"),
                    ze(),
                    He(4, "p"),
                    Cn(5, "Tienda de tecnolog\xeda"),
                    ze()(),
                    He(6, "main"),
                    gr(7, "app-status-checker"),
                    ze(),
                    gr(8, "router-outlet"),
                    ze());
                },
                dependencies: [op, oH],
                styles: [
                  ".container[_ngcontent-%COMP%]{max-width:1200px;margin:0 auto;padding:20px}.app-header[_ngcontent-%COMP%]{text-align:center;margin-bottom:30px}.app-header[_ngcontent-%COMP%]   h1[_ngcontent-%COMP%]{font-size:2.5rem;margin-bottom:10px;color:#3f51b5}.app-header[_ngcontent-%COMP%]   p[_ngcontent-%COMP%]{font-size:1.2rem;color:#666}main[_ngcontent-%COMP%]{padding:20px}",
                ],
              });
            }
          }
          return e;
        })(),
        lH = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵmod = Be({ type: e });
            }
            static {
              this.ɵinj = Ne({ imports: [rh, Pn] });
            }
          }
          return e;
        })(),
        uH = (() => {
          class e {
            static {
              this.ɵfac = function (r) {
                return new (r || e)();
              };
            }
            static {
              this.ɵmod = Be({ type: e, bootstrap: [sH] });
            }
            static {
              this.ɵinj = Ne({ imports: [SD, h$, sj, Aj, NU, $U, tH, lH] });
            }
          }
          return e;
        })();
      rL()
        .bootstrapModule(uH)
        .catch((e) => console.error(e));
    },
  },
  (ne) => {
    ne((ne.s = 272));
  },
]);
