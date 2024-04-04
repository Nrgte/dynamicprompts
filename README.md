### Requirements

- Only tested with A1111 v.1.5.1
- Requires this commit of the webui https://github.com/adieyal/sd-dynamic-prompts/commit/39c06b30409df6259c4430338123f7d4e05d8dc1

### Installation

1. Delete the existing folder: venv\Lib\site-packages\dynamicprompts
2. Copy the content of the src\dynamicprompts_ng folder into venv\Lib\site-packages\dynamicprompts


### Regex variable replacement

$${"${variable_name}", "regex_search_string", "replacement_string"}

replacement_string cannot be an empty string. It needs 1 character at least.
