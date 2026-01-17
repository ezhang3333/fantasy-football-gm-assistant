import './css/ModelFilter.css'

export default function ModelFilter({ name, label, value, onChange, min, max, step }) {
  const id = `param-${name}`;

  return (
    <div className="filter-container">
      <label className="filter-label" htmlFor={id}>{label}</label>
      <input
        className="filter-input"
        id={id}
        name={name}
        type="number"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(name, e.target.value)}
      />
    </div>
  );
}