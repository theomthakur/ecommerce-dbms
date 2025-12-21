-- Macro: safe_cast
-- Safely casts values with error handling

{% macro safe_cast(field, to_type) %}
    try_cast({{ field }} as {{ to_type }})
{% endmacro %}
