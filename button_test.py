# -*- coding: utf-8 -*-
"""This is a test program."""

import streamlit as st

st.header('st.button')

if st.button('Say hello'):
    st.write('Why hello there')
else:
    st.write('Goodbye')
