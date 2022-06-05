# trading

To update book:
1. Write or edit blog post
2. cd to repo root
3. Update `_toc.yml` if needed
4. Run `jupyter-book build .`  You can then preview your stuff in the `_build/html directory`
5. Push changes to git
6. Run `ghp-import -n -p -f _build/html`
