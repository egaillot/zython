# -*- coding: utf-8 -*-
from django import forms
from.models import StockMalt, StockHop, StockYeast


class StockMaltForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StockMaltForm, self).__init__(*args, **kwargs)
        self.fields["malt"].widget.attrs["class"] = "select2"

    class Meta:
        model = StockMalt
        fields = ('malt', 'amount', 'notes')


class StockHopForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StockHopForm, self).__init__(*args, **kwargs)
        self.fields["hop"].widget.attrs["class"] = "select2"

    class Meta:
        model = StockHop
        fields = ('hop', 'amount', 'notes')


class StockYeastForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StockYeastForm, self).__init__(*args, **kwargs)
        self.fields["yeast"].widget.attrs["class"] = "select2"

    class Meta:
        model = StockYeast
        fields = ('yeast', 'amount', 'notes')
