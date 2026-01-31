import "./css/DropdownFilter.css";

export default function DropdownFilter({
  name,
  label,
  value,
  onChange,
  options = [],
  id,
  containerClassName = "filter-container",
  labelClassName = "filter-label",
  selectClassName = "filter-select",
}) {
  const selectId = id ?? `filter-${name}`;
  const normalizedOptions = options.map((option) =>
    typeof option === "string" ? { value: option, label: option } : option
  );

  return (
    <div className={containerClassName}>
      <label className={labelClassName} htmlFor={selectId}>
        {label}
      </label>
      <select
        id={selectId}
        name={name}
        className={selectClassName}
        value={value}
        onChange={(e) => onChange(name, e.target.value)}
      >
        {normalizedOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
