# Knowledge state summary

Generated from `graph.json` (source commit `fc91a833f0d38d9aa95bee850a1301ec1c4bc3d4`). Scope: PEPs whose Topic header contains 'Typing'.

## Counts

| Node type | Count |
|---|---|
| Feature | 43 |
| PEP | 49 |
| PythonVersion | 12 |

| Edge type | Count | Meaning |
|---|---|---|
| available_from | 43 | First version with the feature, taken from the introducing PEP's Python-Version header. |
| builds_on | 108 | Mentioned in Abstract/Motivation/Rationale/Specification-type sections. |
| cites | 39 | Mentioned anywhere else (references, open issues, how to teach, ...). |
| compat_concern | 8 | Mentioned in a Backwards Compatibility-type section. |
| falls_back_to | 18 | Older substitute; edge carries the condition under which it is valid. |
| introduced_by | 43 | The PEP that added this feature. |
| next_version | 11 | Release order. |
| pep_requires | 1 | From the Requires header. |
| rejected_idea_ref | 30 | Mentioned inside a rejected idea or alternative. |
| replaces | 2 | From the Replaces header. |
| requires | 10 | Cannot be used without the target feature. |
| superseded_by | 2 | From the Superseded-By header. |

## Features

| Feature | Introduced by | Python | Requires | Falls back to |
|---|---|---|---|---|
| Callable[[Args], Ret] | PEP 484 (Final) | 3.5 | - | - |
| Implicit type alias (Vector = list[float]) | PEP 484 (Final) | 3.5 | - | - |
| Optional[X] | PEP 484 (Final) | 3.5 | - | - |
| String forward references | PEP 484 (Final) | 3.5 | - | - |
| Type comments (# type: int) | PEP 484 (Final) | 3.5 | - | - |
| TypeVar and Generic classes | PEP 484 (Final) | 3.5 | - | - |
| Union[X, Y] | PEP 484 (Final) | 3.5 | - | - |
| typing.List / Dict / Tuple | PEP 484 (Final) | 3.5 | - | - |
| Variable annotations (x: int = 0) | PEP 526 (Final) | 3.6 | - | Type comments (# type: int) |
| from __future__ import annotations | PEP 563 (Superseded) | 3.7 | - | String forward references |
| py.typed marker and stub packages | PEP 561 (Final) | 3.7 | - | - |
| Final and @final | PEP 591 (Final) | 3.8 | - | - |
| Literal types | PEP 586 (Final) | 3.8 | - | - |
| Protocol (structural subtyping) | PEP 544 (Final) | 3.8 | - | - |
| TypedDict | PEP 589 (Final) | 3.8 | - | - |
| TypedDict total=False | PEP 589 (Final) | 3.8 | TypedDict | - |
| Annotated metadata | PEP 593 (Final) | 3.9 | - | - |
| Built-in generics (list[int], dict[str, int]) | PEP 585 (Final) | 3.9 | - | typing.List / Dict / Tuple, from __future__ import annotations |
| ParamSpec and Concatenate | PEP 612 (Final) | 3.10 | TypeVar and Generic classes | - |
| TypeAlias annotation | PEP 613 (Final) | 3.10 | - | Implicit type alias (Vector = list[float]) |
| TypeGuard | PEP 647 (Final) | 3.10 | - | - |
| X &#124; Y union syntax | PEP 604 (Final) | 3.10 | - | Union[X, Y], from __future__ import annotations |
| @dataclass_transform | PEP 681 (Final) | 3.11 | - | - |
| Arrow callable syntax ((int) -> str) | PEP 677 (Rejected) | 3.11 | - | Callable[[Args], Ret] |
| LiteralString | PEP 675 (Final) | 3.11 | - | - |
| Required / NotRequired TypedDict items | PEP 655 (Final) | 3.11 | TypedDict | TypedDict total=False |
| Self | PEP 673 (Final) | 3.11 | - | TypeVar and Generic classes |
| TypeVarTuple (variadic generics) | PEP 646 (Final) | 3.11 | TypeVar and Generic classes | - |
| @override | PEP 698 (Final) | 3.12 | - | - |
| Type parameter syntax (class Box[T]) | PEP 695 (Final) | 3.12 | - | TypeVar and Generic classes |
| Unpack[TypedDict] for **kwargs | PEP 692 (Final) | 3.12 | TypedDict | - |
| type statement (type Vector = ...) | PEP 695 (Final) | 3.12 | - | TypeAlias annotation |
| @deprecated | PEP 702 (Final) | 3.13 | - | - |
| ReadOnly TypedDict items | PEP 705 (Final) | 3.13 | TypedDict | - |
| Stricter TypeGuard semantics | PEP 724 (Withdrawn) | 3.13 | TypeGuard | TypeIs |
| Type parameter defaults | PEP 696 (Final) | 3.13 | TypeVar and Generic classes | - |
| TypeIs | PEP 742 (Final) | 3.13 | - | TypeGuard |
| Deferred evaluation of annotations (default) | PEP 649 (Final) | 3.14 | - | from __future__ import annotations, String forward references |
| Inline TypedDict (TypedDict[{...}]) | PEP 764 (Draft) | 3.15 | TypedDict | TypedDict |
| ReadOnly class attributes | PEP 767 (Draft) | 3.15 | - | Final and @final |
| TYPE_CHECKING as a built-in | PEP 781 (Draft) | 3.15 | - | - |
| TypeForm | PEP 747 (Final) | 3.15 | - | - |
| TypedDict closed / extra_items | PEP 728 (Final) | 3.15 | TypedDict | - |

## PEP to PEP links (typed by section)

| From | Type | To | Found in sections |
|---|---|---|---|
| PEP 482 | builds_on | PEP 484 | Abstract |
| PEP 483 | builds_on | PEP 484 | Abstract, Notational conventions |
| PEP 484 | builds_on | PEP 482 | Abstract |
| PEP 484 | builds_on | PEP 483 | Abstract |
| PEP 526 | builds_on | PEP 484 | Abstract, Rationale, Specification |
| PEP 544 | builds_on | PEP 483 | Nominal vs structural subtyping |
| PEP 544 | builds_on | PEP 484 | Abstract, Callback protocols, Nominal vs structural subtyping, Non-goals, Protocol members, Rationale and Goals, Recursive protocols, Self-types in protocols |
| PEP 544 | builds_on | PEP 526 | Non-goals, Protocol members |
| PEP 560 | builds_on | PEP 484 | Abstract, Performance, Using __class_getitem__ in C extensions |
| PEP 560 | builds_on | PEP 526 | Abstract |
| PEP 561 | builds_on | PEP 484 | Abstract, Rationale, Specification |
| PEP 563 | builds_on | PEP 484 | Abstract, Non-goals, Non-typing usage of annotations |
| PEP 563 | builds_on | PEP 526 | Abstract, Non-goals, Non-typing usage of annotations |
| PEP 563 | builds_on | PEP 544 | Non-typing usage of annotations |
| PEP 563 | builds_on | PEP 560 | Non-typing usage of annotations |
| PEP 563 | builds_on | PEP 649 | Rationale and Goals |
| PEP 586 | builds_on | PEP 484 | Abstract, Core behavior, Motivation and Rationale |
| PEP 589 | builds_on | PEP 483 | Type Consistency |
| PEP 589 | builds_on | PEP 484 | Abstract, Motivation, Specification, Using TypedDict Types |
| PEP 589 | builds_on | PEP 526 | Alternative Syntax |
| PEP 589 | builds_on | PEP 586 | Use of Final Values and Literal Types |
| PEP 589 | builds_on | PEP 591 | Use of Final Values and Literal Types |
| PEP 591 | builds_on | PEP 586 | The Final annotation |
| PEP 593 | builds_on | PEP 484 | Motivation |
| PEP 604 | builds_on | PEP 484 | Motivation |
| PEP 604 | builds_on | PEP 526 | Motivation |
| PEP 604 | builds_on | PEP 585 | Motivation |
| PEP 612 | builds_on | PEP 484 | Abstract, Motivation |
| PEP 612 | builds_on | PEP 544 | Abstract |
| PEP 613 | builds_on | PEP 484 | Motivation |
| PEP 646 | builds_on | PEP 484 | *args as a Type Variable Tuple, Abstract |
| PEP 649 | builds_on | PEP 484 | A History Of Annotations, Static typing users |
| PEP 649 | builds_on | PEP 526 | A History Of Annotations |
| PEP 649 | builds_on | PEP 563 | A History Of Annotations, Abstract, Comparison Of Annotation Semantics, Documentation, Motivation For This PEP, Overview, Runtime annotation users, Static typing users, Wrappers |
| PEP 655 | builds_on | PEP 589 | Abstract, Interaction with total=False, Motivation, Specification |
| PEP 673 | builds_on | PEP 484 | Abstract |
| PEP 673 | builds_on | PEP 544 | Use in Protocols |
| PEP 675 | builds_on | PEP 586 | Motivation |
| PEP 677 | builds_on | PEP 484 | Background and History, Motivation |
| PEP 677 | builds_on | PEP 585 | Rationale |
| PEP 677 | builds_on | PEP 604 | Additional Behaviors of types.CallableType, Background and History, Precedence of ->, Rationale |
| PEP 677 | builds_on | PEP 612 | Compact Syntax for ParamSpec |
| PEP 677 | builds_on | PEP 646 | Grammar and AST |
| PEP 692 | builds_on | PEP 589 | Rationale |
| PEP 692 | builds_on | PEP 646 | Rationale |
| PEP 692 | builds_on | PEP 655 | Required and non-required keys |
| PEP 695 | builds_on | PEP 483 | Points of Confusion |
| PEP 695 | builds_on | PEP 484 | Constrained Type Specification, Motivation, Points of Confusion, Type Parameter Scopes, Variance Inference |
| PEP 695 | builds_on | PEP 612 | Motivation, Type Parameter Declarations |
| PEP 695 | builds_on | PEP 613 | Generic Type Alias |
| PEP 695 | builds_on | PEP 646 | Motivation, Type Parameter Declarations |
| PEP 696 | builds_on | PEP 646 | TypeVarTuple\ s as Defaults |
| PEP 696 | builds_on | PEP 695 | Abstract, Default Ordering and Subscription Rules |
| PEP 698 | builds_on | PEP 591 | Runtime Override Checks in Python |
| PEP 702 | builds_on | PEP 698 | Specification |
| PEP 705 | builds_on | PEP 544 | Pure functions |
| PEP 705 | builds_on | PEP 589 | Abstract, Alternative functional syntax, Inheritance, Motivation, Type consistency |
| PEP 705 | builds_on | PEP 655 | Interaction with other special types |
| PEP 705 | builds_on | PEP 692 | Keyword argument typing |
| PEP 718 | builds_on | PEP 646 | Functions Parameterized by TypeVarTuple\ s |
| PEP 718 | builds_on | PEP 696 | Binding Rules |
| PEP 718 | builds_on | PEP 747 | Motivation, Rationale |
| PEP 724 | builds_on | PEP 647 | Abstract, Motivation, Specification |
| PEP 727 | builds_on | PEP 484 | Motivation |
| PEP 728 | builds_on | PEP 589 | Specification |
| PEP 728 | builds_on | PEP 692 | Previous Discussions, Support Additional Keys for Unpack |
| PEP 728 | builds_on | PEP 705 | Previous Discussions |
| PEP 729 | builds_on | PEP 484 | It's hard to evolve the specification, Mandate, Motivation, Operations and process, PEPs are the only specification |
| PEP 729 | builds_on | PEP 526 | Operations and process |
| PEP 729 | builds_on | PEP 561 | It's hard to evolve the specification |
| PEP 729 | builds_on | PEP 647 | Operations and process, Relationship with the Steering Council |
| PEP 729 | builds_on | PEP 655 | Relationship with the Steering Council |
| PEP 729 | builds_on | PEP 673 | Relationship with the Steering Council |
| PEP 729 | builds_on | PEP 675 | Relationship with the Steering Council |
| PEP 729 | builds_on | PEP 681 | Operations and process |
| PEP 729 | builds_on | PEP 688 | Operations and process |
| PEP 729 | builds_on | PEP 695 | Operations and process, Relationship with the Steering Council |
| PEP 729 | builds_on | PEP 698 | Relationship with the Steering Council |
| PEP 729 | builds_on | PEP 702 | Operations and process, Relationship with the Steering Council |
| PEP 729 | builds_on | PEP 718 | Relationship with the Steering Council |
| PEP 729 | builds_on | PEP 727 | Relationship with the Steering Council |
| PEP 742 | builds_on | PEP 647 | Motivation |
| PEP 742 | builds_on | PEP 724 | Motivation, Rationale |
| PEP 746 | builds_on | PEP 593 | Motivation |
| PEP 747 | builds_on | PEP 589 | Motivation |
| PEP 749 | builds_on | PEP 563 | Abstract |
| PEP 749 | builds_on | PEP 649 | Abstract, Motivation, Rationale, Specification |
| PEP 749 | builds_on | PEP 695 | Abstract, Specification |
| PEP 749 | builds_on | PEP 696 | Abstract, Specification |
| PEP 764 | builds_on | PEP 589 | Abstract |
| PEP 767 | builds_on | PEP 705 | Abstract, Interaction with Other Type Qualifiers, Rationale, Subtyping |
| PEP 781 | builds_on | PEP 484 | Motivation |
| PEP 781 | builds_on | PEP 563 | Motivation |
| PEP 781 | builds_on | PEP 649 | Motivation |
| PEP 821 | builds_on | PEP 646 | Design goals |
| PEP 821 | builds_on | PEP 692 | Design goals, Semantics |
| PEP 821 | builds_on | PEP 728 | Design goals, Semantics |
| PEP 827 | builds_on | PEP 612 | More powerful decorator typing |
| PEP 827 | builds_on | PEP 646 | Unpack of typevars for **kwargs |
| PEP 827 | builds_on | PEP 681 | Motivation, dataclasses-style method generation |
| PEP 827 | builds_on | PEP 692 | Unpack of typevars for **kwargs |
| PEP 835 | builds_on | PEP 585 | Historical Context and Prior Art |
| PEP 835 | builds_on | PEP 593 | Motivation |
| PEP 835 | builds_on | PEP 604 | Historical Context and Prior Art, Operator Precedence |
| PEP 835 | builds_on | PEP 727 | Motivation |
| PEP 846 | builds_on | PEP 695 | Motivation |
| PEP 849 | builds_on | PEP 586 | Motivation |
| PEP 849 | builds_on | PEP 827 | Motivation |
| PEP 483 | cites | PEP 484 | Covariance and Contravariance, Pragmatics, Types vs. Classes |
| PEP 484 | cites | PEP 482 | Acknowledgements |
| PEP 484 | cites | PEP 483 | Covariance and contravariance |
| PEP 484 | cites | PEP 526 | Type comments |
| PEP 484 | cites | PEP 561 | Storing and distributing stub files |
| PEP 526 | cites | PEP 484 | Changes to Standard Library and Documentation |
| PEP 544 | cites | PEP 483 | Unions and intersections of protocols |
| PEP 544 | cites | PEP 484 | Using Protocols in Python 2.7 - 3.5 |
| PEP 561 | cites | PEP 526 | Definition of Terms |
| PEP 563 | cites | PEP 484 | In PEP 484, python/typing#400 |
| PEP 563 | cites | PEP 526 | Implementation |
| PEP 563 | cites | PEP 649 | Resolution |
| PEP 563 | cites | PEP 749 | Resolution |
| PEP 585 | cites | PEP 563 | Implementation |
| PEP 586 | cites | PEP 484 | Illegal parameters for Literal at type check time, Interactions with enums and exhaustiveness checks |
| PEP 586 | cites | PEP 591 | Interactions with Final |
| PEP 649 | cites | PEP 563 | Acknowledgements, Annotations On Local Variables Inside Functions, Performance Comparison |
| PEP 695 | cites | PEP 563 | Lazy Evaluation |
| PEP 695 | cites | PEP 649 | Lazy Evaluation |
| PEP 696 | cites | PEP 695 | Grammar changes |
| PEP 724 | cites | PEP 483 | Footnotes |
| PEP 727 | cites | PEP 702 | Documentation is not Typing |
| PEP 728 | cites | PEP 705 | Acknowledgments |
| PEP 742 | cites | PEP 724 | Acknowledgments |
| PEP 747 | cites | PEP 649 | Footnotes |
| PEP 749 | cites | PEP 563 | The future of from __future__ import annotations |
| PEP 749 | cites | PEP 649 | Acknowledgments, Adding the VALUE_WITH_FAKE_GLOBALS format, Behavior of the REPL, Caching of annotations on partially executed modules, Conditionally defined annotations, Deferred evaluation of PEP 695 and 696 objects, Effect of deleting __annotations__, How to Teach This, Metaclass behavior with PEP 649, Miscellaneous implementation details, New annotationlib module, Security Implications, Signature of __annotate__ functions, Supported operations on ForwardRef objects, The future of from __future__ import annotations, Which expressions can be stringified?, Wrappers that provide __annotations__ |
| PEP 749 | cites | PEP 695 | Deferred evaluation of PEP 695 and 696 objects |
| PEP 749 | cites | PEP 696 | Deferred evaluation of PEP 695 and 696 objects |
| PEP 764 | cites | PEP 728 | Inline typed dictionaries and extra items |
| PEP 767 | cites | PEP 705 | How to Teach This |
| PEP 821 | cites | PEP 677 | References |
| PEP 821 | cites | PEP 692 | References |
| PEP 821 | cites | PEP 728 | How to Teach This, References |
| PEP 827 | cites | PEP 764 | Dictionary comprehension based syntax for creating typed dicts and protocols |
| PEP 835 | cites | PEP 484 | Terminology |
| PEP 835 | cites | PEP 593 | Terminology |
| PEP 835 | cites | PEP 727 | References |
| PEP 835 | cites | PEP 746 | Targeted Metadata, Terminology |
| PEP 563 | compat_concern | PEP 649 | Deprecation policy |
| PEP 649 | compat_concern | PEP 563 | Backwards Compatibility With PEP 563 Semantics, Backwards Compatibility With Stock Semantics |
| PEP 675 | compat_concern | PEP 586 | Backwards Compatibility |
| PEP 677 | compat_concern | PEP 612 | Incompatibility with other possible uses of * and ** |
| PEP 677 | compat_concern | PEP 646 | Incompatibility with other possible uses of * and ** |
| PEP 749 | compat_concern | PEP 563 | Backwards Compatibility |
| PEP 749 | compat_concern | PEP 649 | Backwards Compatibility |
| PEP 827 | compat_concern | PEP 649 | Backwards Compatibility |
| PEP 749 | pep_requires | PEP 649 | Requires header of PEP 749 |
| PEP 484 | rejected_idea_ref | PEP 563 | The problem of forward declarations, What about existing uses of annotations? |
| PEP 526 | rejected_idea_ref | PEP 484 | Rejected/Postponed Proposals |
| PEP 544 | rejected_idea_ref | PEP 484 | Allow only protocol methods and force use of getters and setters, Overriding inferred variance of protocol classes, Support adapters and adaptation |
| PEP 544 | rejected_idea_ref | PEP 526 | Make protocols interoperable with other approaches |
| PEP 586 | rejected_idea_ref | PEP 484 | True dependent types/integer generics |
| PEP 589 | rejected_idea_ref | PEP 484 | Rejected Alternatives |
| PEP 604 | rejected_idea_ref | PEP 563 | 2. Change only PEP 484 (Type hints) to accept the syntax type1 &#124; type2 ? |
| PEP 649 | rejected_idea_ref | PEP 563 | Mistaken Rejection Of This Approach In November 2017 |
| PEP 655 | rejected_idea_ref | PEP 604 | Replace Optional with Nullable. Repurpose Optional to mean “optional item”. |
| PEP 677 | rejected_idea_ref | PEP 585 | Improving Usability of the Indexed Callable Type |
| PEP 677 | rejected_idea_ref | PEP 612 | Extended Syntax Supporting Named and Optional Arguments, Rejected Alternatives, Syntax Closer to Function Signatures |
| PEP 677 | rejected_idea_ref | PEP 646 | Rejected Alternatives |
| PEP 681 | rejected_idea_ref | PEP 526 | auto_attribs parameter |
| PEP 688 | rejected_idea_ref | PEP 544 | Keep bytearray compatible with bytes |
| PEP 705 | rejected_idea_ref | PEP 591 | Preventing unspecified keys in TypedDicts, Reusing the Final annotation |
| PEP 705 | rejected_idea_ref | PEP 728 | Preventing unspecified keys in TypedDicts |
| PEP 727 | rejected_idea_ref | PEP 702 | Extra Metadata and Decorator |
| PEP 729 | rejected_idea_ref | PEP 484 | Writing the specification from scratch |
| PEP 742 | rejected_idea_ref | PEP 647 | Change the behavior of TypeGuard |
| PEP 742 | rejected_idea_ref | PEP 724 | Alternative names, Change the behavior of TypeGuard, Do nothing |
| PEP 746 | rejected_idea_ref | PEP 695 | Introducing a type variable instead of a generic class |
| PEP 749 | rejected_idea_ref | PEP 649 | Rejected alternatives |
| PEP 764 | rejected_idea_ref | PEP 585 | Using dict or typing.Dict with a single type argument |
| PEP 764 | rejected_idea_ref | PEP 604 | Using a simple dictionary |
| PEP 821 | rejected_idea_ref | PEP 612 | Rejected Ideas |
| PEP 821 | rejected_idea_ref | PEP 677 | Alternatives considered |
| PEP 821 | rejected_idea_ref | PEP 692 | Alternatives considered |
| PEP 835 | rejected_idea_ref | PEP 593 | Sole Reliance on __rmatmul__ |
| PEP 835 | rejected_idea_ref | PEP 749 | Structural Evaluation Format (Format.TYPE) |
| PEP 849 | rejected_idea_ref | PEP 649 | Storing Annotation Source Code |
| PEP 649 | replaces | PEP 563 | Replaces header of PEP 649 |
| PEP 742 | replaces | PEP 724 | Replaces header of PEP 742 |
| PEP 563 | superseded_by | PEP 649 | Superseded-By header of PEP 563 |
| PEP 563 | superseded_by | PEP 749 | Superseded-By header of PEP 563 |
