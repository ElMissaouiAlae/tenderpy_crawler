# Fix: parser only extracts the first tender row per page

## Root cause

`SearchResultParser.parse()` finds the results table via
`extract_table()` (`th#cons_ref` -> `find_parent("table")`), then calls
`extract_rows(table)`, which does `table.find_all("tr")` and filters for
rows containing a `td[headers="cons_ref"]` cell.

The live site emits two unclosed `<div>` elements inside **every** row:

```html
<div id="identification_cons_N">                 <!-- never closed -->
<div id="identification_cons_N_lieuxExecution">   <!-- never closed -->
```

Confirmed against a captured real response: whole-document `<div>` open
count is 435 vs. 415 close — a 20-tag deficit, i.e. exactly 2 unclosed
`div`s x 10 rows on a 10-row page.

Browsers tolerate this fine (HTML5 tree construction auto-closes /
foster-parents mis-nested tags). `BeautifulSoup(html, "html.parser")`
does not implement that recovery — it builds a literal nesting stack.
Because row 1's two `div`s never close, every tag that follows in the
document (rows 2-10, and the rest of the page) becomes a **descendant**
of row 1's div instead of a sibling `<tr>` under `<table>`.

Net effect: the `<table>` tag itself is fine (opens once, closes once),
but the `Tag` object BS4 builds for it only "contains" the header row
and row 1 as children — `table.find_all("tr")` never sees rows 2-10,
because they aren't attached to the table node in the (malformed) parse
tree, even though the raw markup is one flat table.

Verified fix direction: searching **the whole document** for
`td[headers="cons_ref"]` and walking up to each one's own `<tr>` finds
all 10 rows regardless of the broken tree shape:

```python
tds = soup.find_all("td", headers="cons_ref")
rows = [td.find_parent("tr") for td in tds]
```

This needs no new dependency (no `lxml`/`html5lib` swap) and requires
only a change to how rows are located, not to the individual field
extractors (`extract_tender` and its helpers already operate correctly
per-row).

## Implementation steps

1. **Reproduce with a regression test first (TDD)**
   - `tests/test_parser.py` already has a fixture (`HTML_TABLE`) built
     from real captured markup with the same unclosed-`div` pattern and
     3 rows.
   - Confirm `test_extract_rows_returns_all_rows_from_real_page_chunk`
     and `test_parse_extracts_every_tender_from_real_page_chunk`
     currently **fail** (only 1 row/tender extracted instead of 3).
     These are the tests the fix must turn green — no new fixture
     needed.

2. **Change `extract_rows` to search from the document root, not from
   the table node**
   - Current signature: `extract_rows(self, table: Any) -> list[Any]`.
   - New approach: find all `td[headers="cons_ref"]` cells directly
     (searched from the soup/document, not scoped to a `table` Tag),
     then return each cell's parent `<tr>` (`td.find_parent("tr")`).
   - Preserve existing filtering semantics: skip rows that are actually
     header rows (i.e. keep the "no `<th>` in this row" guard) and skip
     any `td.find_parent("tr")` that returns `None`.
   - Decide the new signature:
     - Preferred: `extract_rows(self, soup: BeautifulSoup) -> list[Any]`
       — operates on the whole parsed document since that's the only
       thing that reliably contains every row regardless of tree
       damage.

3. **Remove `extract_table`, since it becomes unnecessary**
   - Its only caller is `parse()`, and its only purpose was to hand a
     `table` Tag to `extract_rows`. Once `extract_rows` searches the
     document directly, `extract_table` has no remaining purpose.
   - Delete the method and its call site in `parse()`.
   - Check `extract_pagination` and the rest of `parse()` — they
     already operate on `soup` directly and don't depend on
     `extract_table`, so no other change needed there.

4. **Update `parse()`**
   - Replace:
     ```python
     table = self.extract_table(soup)
     rows = self.extract_rows(table)
     ```
     with:
     ```python
     rows = self.extract_rows(soup)
     ```

5. **Update existing tests to match the new contract**
   - `test_extract_table_finds_table_by_cons_ref_header` — delete (the
     method it tests no longer exists).
   - `test_extract_rows_returns_only_data_rows_with_cons_ref_cell` —
     update to call `parser.extract_rows(soup)` instead of
     `parser.extract_rows(table)` (drop the
     `table = parser.extract_table(soup)` step).
   - `test_extract_rows_returns_all_rows_from_real_page_chunk` — same
     change: call `parser.extract_rows(soup)` instead of passing
     `soup.find("table")`.
   - `test_search_result_parser_handles_missing_table` — rename to
     reflect "no results table in the HTML" rather than "table not
     found", but behavior (`page.tenders == []`) should still hold
     since there's no `td[headers="cons_ref"]` in that fixture either.

6. **Run the full test suite and confirm**
   - `tests/test_parser.py` — all tests green, especially the two
     "real page chunk" tests (3/3 tenders, correct `tender_id` and
     `reference_number` order).
   - `integration_test.py` (or a targeted manual run of
     `DiscoveryClient.search()` against the live site) — confirm the
     tenders-parsed count now matches the 10-per-page count the site
     reports, not 1.

7. **Sanity-check downstream consumers**
   - `DiscoveryClient._build_row_echo_payload` iterates
     `page.tenders` by index to rebuild `ctl{i}$refCons` /
     `ctl{i}$orgCons` hidden fields for the next postback. With all 10
     rows now present, confirm the index numbering (`ctl1`..`ctl10`)
     still lines up with what PRADO expects on `next_page()` — this
     was previously masked because only 1 row was ever echoed back.
   - Re-run pagination (`search_all` / `next_page`) against the live
     site for at least 2-3 pages to confirm the fix doesn't break the
     postback contract now that more rows are echoed.

## Out of scope / not needed for this fix

- Swapping the BeautifulSoup parser backend to `lxml` or `html5lib`.
  Would also fix this by giving BS4 a spec-compliant HTML5 tree
  builder, but it's a new dependency for a problem that's solvable by
  not relying on the table's child structure in the first place.
- Any changes to `extract_tender` or its field-level helpers
  (`_extract_hidden_value`, `_extract_by_id_suffix`,
  `_extract_labeled_block`, etc.) — these already operate correctly on
  a single row once handed the right `<tr>`.
