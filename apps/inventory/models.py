# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from brew.models import Malt, Hop, Yeast


class BaseUserStock(models.Model):
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(_(u"Notes, mémos..."), null=True, blank=True)

    class Meta:
        abstract = True


class StockMalt(BaseUserStock):
    malt = models.ForeignKey(Malt)
    amount = models.DecimalField(max_digits=5, decimal_places=2, help_text="kg")


class StockHop(BaseUserStock):
    hop = models.ForeignKey(Hop)
    amount = models.DecimalField(max_digits=6, decimal_places=2, help_text="g")


class StockYeast(BaseUserStock):
    malt = models.ForeignKey(Yeast)
    amount = models.DecimalField(max_digits=6, decimal_places=2, help_text="g")
