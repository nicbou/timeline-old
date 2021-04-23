import logging
from typing import List, Iterable

from django.apps import apps
from django.db import models

logger = logging.getLogger(__name__)


def get_models_by_name(class_names: Iterable[str]) -> List[models.Model]:
    """
    Return all Django models that match a list of class names. It also returns models whose parents match that classname
    """
    matching_models = []
    for model in apps.get_models():
        parent_class_names = set([parent.__name__ for parent in model.mro()])
        if parent_class_names.intersection(class_names):
            matching_models.append(model)
    return matching_models
