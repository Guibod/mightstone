from typing import Optional

from assertpy import assert_that
from pydantic import BaseModel

from mightstone.common import pydantic_model_recurse


class A(BaseModel):
    id: int
    items: list[BaseModel] = []
    is_eligible: bool = False


class B(BaseModel):
    id: int
    item: Optional[BaseModel] = None
    is_eligible: bool = False


class C(BaseModel):
    id: int
    items: dict[str, BaseModel] = {}
    is_eligible: bool = False


structure = A(
    id=0,
    is_eligible=True,
    items=[
        A(id=1),
        B(id=2),
        A(id=3, is_eligible=True),
        A(id=4, items=[B(id=6, item=B(id=11, is_eligible=True))]),
        A(
            id=5,
            items=[
                A(id=7, is_eligible=True),
                B(id=8),
                C(
                    id=9,
                    items={"twelve": A(id=12), "thirteen": B(id=13, is_eligible=True)},
                ),
            ],
        ),
        C(id=666),
    ],
)


def test_recursively_extract_is_instance():
    extracted = list(pydantic_model_recurse(structure, lambda x: isinstance(x, B)))
    ids = [x.id for x in extracted]

    assert_that(all(isinstance(extr, B) for extr in extracted)).is_true()

    assert_that(ids).contains(2)
    assert_that(ids).contains(6)
    assert_that(ids).contains(8)
    assert_that(ids).contains(11)
    assert_that(ids).contains(13)
    assert_that(extracted).is_length(5)


def test_recursively_extract_is_has_property():
    extracted = list(pydantic_model_recurse(structure, lambda x: x.is_eligible))
    ids = [x.id for x in extracted]

    assert_that(all(extr.is_eligible for extr in extracted)).is_true()

    assert_that(ids).contains(0)
    assert_that(ids).contains(3)
    assert_that(ids).contains(7)
    assert_that(ids).contains(11)
    assert_that(ids).contains(13)
    assert_that(extracted).is_length(5)
