# Zarr: how to represent arrays whose chunks use different codecs (zarr-specs#399)

- Source: https://github.com/zarr-developers/zarr-specs/issues/399 "Varying codec parameters per-chunk" (open, opened 2026-10-12 by TomNicholas, marked MEMBER; 19 comments when read, last on 2026-10-17)
- Items it links to, state checked through the GitHub API on 2026-10-18:
  - https://github.com/zarr-developers/VirtualiZarr/issues/1111 "Concatenate arrays with padded final chunks" (open)
  - https://github.com/zarr-developers/VirtualiZarr/issues/1078 "Dangling pixel concatenation (variable-length chunks)" (open)
  - https://github.com/zarr-developers/VirtualiZarr/issues/217 (open, a use case from an ocean model's output)
  - https://github.com/zarr-developers/zarr-specs/issues/288 "Zarr extension for stacked / concatenated virtual views" (open)
  - https://github.com/zarr-developers/zarr-extensions/pull/27 "feat: add conditional codec" (merged 2025-10-28)
  - https://github.com/d-v-b/refkv/pull/73 (open, a documented proof-of-concept by a commenter, opened 2026-10-14)

Zarr is a format for chunked, compressed arrays. A "codec" is the step that encodes or compresses a chunk. VirtualiZarr and Icechunk let people treat many existing files (for example NetCDF) as one Zarr array without copying the data. This thread is a design discussion, not a bug. I summarise it and did not test any code.

## The problem (author's statement)
The author says virtualising many real archives fails when files differ in subtle ways, and that two things block it: chunks of varying length ("rectilinear chunks"), and different codecs for different chunks. Virtualising varying chunk lengths often needs varying codecs too, because the internal chunk shapes vary per file. Zarr arrays today fix one codec chain per array. His use cases include a satellite dataset whose codec changed over time, files whose size varies along time, parallel simulation output where edge processes write bigger regions, and one dataset where every file uses a different scale factor and offset (he calls it "insane"). He says he must have one logical array with one dtype, parallel decoding, and a readable `zarr.json`.

## The options he laid out
1. Array concatenation: a convention for defining an array as a concatenation of other arrays. Listed pros: no spec change. Listed cons include leaking physical layout into the logical array, not failing gracefully in readers that do not understand it, and not composing with other operations.
2. A "parametrized codec": one codec that holds several codec chains and picks one per chunk. The hard part is giving it per-chunk context. He suggests either the store prepends the chunk index to the bytes, or a codec fetches per-chunk parameters from a manifest, much as the sharding codec does its own I/O. He lists cons including abusing codecs.
3. A Zarr 3.2 that allows per-chunk metadata, which his headline says is the third way. I read this part only through the summary and comments, not the full text.

## What others said (attributed)
- mkitti (CONTRIBUTOR) pointed out a "conditional codec" that was merged without a schema, and that HDF5 has a per-chunk filter mask, so some way of doing this is needed to mimic HDF5. He thinks per-chunk change is big enough to be called Zarr v4, or could be a separate storage-transformer specification.
- d-v-b (CONTRIBUTOR) suggested no spec change: let the store return bytes made by concatenating a short inline byte string (holding the per-chunk parameters) with a byte-range reference to the chunk, with a custom codec that reads that prefix. He later linked a proof-of-concept pull request in his own repository. jbms (CONTRIBUTOR) backed that direction and said it needs no change to the Zarr data model, though any approach needs something implemented in every reader.
- ianhi (CONTRIBUTOR) and TomNicholas asked how that differs from option 2. Tom said that if it is all hidden behind the store, he could implement it using Icechunk manifests however he likes. jbms replied he wanted Icechunk to stay generic, dealing only in bytes.
- ghidalgo3 (no repository association) argued that the worst case, with every chunk unique, makes every option need metadata proportional to the number of chunks, and liked the idea of per-chunk summary statistics for predicate pushdown. That is his opinion.
- d-v-b also noted a union data type could express an array holding different types.

## Where it stands
No decision. The thread is still two views: change the spec to allow per-chunk metadata, or keep the spec and extend how references and stores work. I did not see a maintainer ruling in the comments I read.

## Honest limits
- I read the opening post up to the start of option 3's text and most comments, and I did not read every comment's full text. Some technical details may be off at the edges.
- I did not check the proof-of-concept code or the conditional codec's behaviour.
- I do not know how many real datasets are affected beyond the author's list.
