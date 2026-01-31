import './css/ModelFilter.css'
import { Plus, Minus } from "lucide-react"

export default function ModelFilter({ name, label, value, onChange, min, max, step }) {
  const id = `param-${name}`;

  return (
    <div className="filter-container">
      <label className="filter-label" htmlFor={id}>{label}</label>
      <Plus className="plus-sign" size={20}/>
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
      <Minus className="minus-sign" size={20}/>
    </div>
  );
}