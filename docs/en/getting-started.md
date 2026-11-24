# Get started with Embedded Hardware

[Tiếng Việt](../vi/getting-started.md) · [Documentation](index.md)

The [controller](../../rtl/experiment-controller/top.v) implements the Lab-First permit and fault scaffold. The [instrument interface](../../rtl/instrument/top.v) keeps unqualified instrument requests and availability deasserted. The [testbenches](../../verification/rtl/) exercise both modules.

Node packages the source and its inventory. Python 3.14 with slang and the pinned Icarus distribution runs [isolated verification](verification.md).
