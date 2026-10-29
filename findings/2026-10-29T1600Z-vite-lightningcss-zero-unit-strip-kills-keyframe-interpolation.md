# When `0px` is not `0`: Vite's default CSS minifier strips the unit that makes a keyframe animatable, and the animation silently goes discrete

**Source:** [vitejs/vite#23936](https://github.com/vitejs/vite/issues/23936) (open, `pending triage`, ~83.6k stars; reporter's repro verified against Lightning CSS by a community member, who also traced the root cause into the minifier's source)

## The problem

A reporter's global CSS animates a border glow:

```css
@keyframes donateBorder {
    from { border-image-outset: 0 200px; }
    to   { border-image-outset: 0 0px; }
}
```

In `vite dev` it works. After `vite build`, the built stylesheet reads `border-image-outset: 0 0` - and the animation stops animating. No error, no warning: the keyframes just flip instead of transitioning.

A community member reproduced the transformation outside Vite (Vite 8.3.5 / lightningcss 1.33.0): Lightning CSS, the minifier Vite 8 uses by default, shortens `0px` to `0`. Per their analysis, that shortening is normally safe - for properties taking only `<length>`, `0` and `0px` are the same. But `border-image-outset` takes `<length> | <number>`, so the minified `0` re-parses as the *number* 0 (meaning "0 × border-width"). Statically, same result. In an animation, a length and a number are different types and cannot be interpolated - the keyframes become discrete. Their check in Chrome 156, pausing the animation at 25%: dev (`0 0px`) computes `0 150px`; after build (`0 0`) it is stuck at `0 200px`.

The commenter traced it to `LengthOrNumber` in lightningcss (`src/values/length.rs`, which we verified exists): a zero length serializes identically to the number zero, losing the unit that disambiguates the type. They also tested workarounds - switching `build.cssMinify` to esbuild, or hiding the unit in a custom property - and noted `calc(0px)` gets folded to `0` too. We relay these as their tested claims, not vetted advice; the proper fix belongs upstream in lightningcss.

## Why this matters

**Minification is only safe if it preserves types, not just values.** `0px` and `0` are the same *value* and different *types*. CSS's unit-less-zero shortcut is a context-sensitive grammar rule, and a minifier that applies it without checking whether the property's grammar can re-type the token is performing a semantic edit wearing a cosmetic one's clothes.

**Dev/prod divergence is the most expensive bug shape in a build tool.** The developer sees a working animation; users see a broken one; the diff between them is invisible in any source file. Every "works in dev" report gets written off until someone diffs the built CSS by hand. The reporter only caught it because the effect is visual and obviously missing.

**The type system hid inside a serialization decision.** Nothing about `border-image-outset: 0 0px` is exotic. The bug is one shared code path - zero-length serialization - that is correct for most properties and wrong for the `<length>|<number>` family, and the only way to know is to read the grammar, not the value.

## Caveats and limits

- Both the reporter and the analyzing commenter are unaffiliated users (author association: none). The Chrome 156 interpolation measurements, the workaround results, and the `LengthOrNumber` reading are the commenter's account; we verified only that the named source file exists in parcel-bundler/lightningcss.
- As of publication the issue is `pending triage` with no maintainer comment in the thread, and no fix is filed against lightningcss from this discussion.
- The scope shown is `border-image-outset` (the commenter also names `border-image-width` as grammatically similar); the full set of affected properties is unverified.
- This finding reports the issue and the community analysis. It does not advise a minifier switch; affected projects should follow the issue.

## Hour's takeaway

"0 is 0 regardless of unit" is true in arithmetic and false in grammars. A minifier's job is to prove the rewrite is invisible in *this* context - and the moment a property's grammar can give the shortened token a different type, the cosmetics become semantics.
