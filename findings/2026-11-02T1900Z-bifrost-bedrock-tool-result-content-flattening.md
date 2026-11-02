# Bifrost: the Bedrock ingress flattens a tool result to its first JSON or text member - images, documents and later text blocks silently vanish

**Source:** https://github.com/maximhq/bifrost/issues/9516 (opened 2026-11-02, open, no maintainer reply yet)

## The problem

Bifrost is an open-source LLM gateway (~9.3k stars). On its AWS-Bedrock-shaped routes - `POST /bedrock/model/{modelId}/invoke`, `/invoke-with-response-stream`, `/converse` and `/converse-stream` - a multi-part tool result is reduced to a single string before it reaches the model. In `convertSingleBedrockMessageToBifrostMessages` (`core/providers/bedrock/responses.go`), the tool-result branch takes the first `json` member of the content array, or failing that the first `text` member, and discards everything else: `image` blocks, `document` blocks, and any text after the first. The HTTP answer is still 200, and the model answers as if the tool returned less than it did. Agents whose tools return screenshots, rendered PDF pages or files lose that content on every such call.

The same payload sent through the `/anthropic/v1/messages` route keeps its full content, so only the Bedrock-shaped ingress is affected. The reporter reproduced it on the latest release (`transports/v2.4.0`) and reports the code is unchanged on the development branch. The issue cross-references a sibling report about document blocks dropped by the invoke decoder (#9308, whose proposed fix #9376 is still open and explicitly does not cover this conversion branch) - the flattening reported here is independent: it also affects the Converse routes and images, which the decoder path keeps.

## Verification

The cited code does what the report claims: at tag `transports/v2.4.0`, the tool-result branch of the converter builds a single output string by scanning for the first JSON member and then the first text member, and sets `ResponsesToolCallOutputStr` to it; the only escape is an envelope encoding that per the report applies to search-result/video members. The related issue #9308 and open PR #9376 exist as described. This finding verified those anchors directly.

## Why it matters

This is a silent data-loss bug on a proxy boundary: the client sends valid content, the gateway drops most of it, and both sides see success. It disproportionately hits exactly the workloads Bedrock's Converse API added multi-modal tool results for - vision agents reading screenshots and document pipelines - and it is route-dependent, so the same agent works on one endpoint and degrades on another with no error anywhere.

## Caveats

- Open with no maintainer response; the only engagement so far is an automated issue-planner bot. The reporter's association is NONE, but the report includes a self-contained reproduction script and version-pinned code references, and the key ones check out against the published source.
- This reports the upstream report and verified code anchors; it does not re-run the gateway and does not propose a specific patch.
