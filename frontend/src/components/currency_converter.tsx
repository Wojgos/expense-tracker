import { useState } from "react";
import toast from "react-hot-toast";
import { useCurrencyConvert } from "../hooks/use_currency";

const currencies = ["PLN", "EUR", "USD", "GBP", "CHF", "CZK"];

export default function CurrencyConverter() {
  const [amount, setAmount] = useState("100");
  const [base, setBase] = useState("EUR");
  const [target, setTarget] = useState("PLN");
  const convert = useCurrencyConvert();

  const handleConvert = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await convert.mutateAsync({ amount, base, target });
    } catch {
      toast.error("Conversion failed — exchange rate unavailable");
    }
  };

  return (
    <section>
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wider text-gray-400">
        Currency Converter
      </h3>
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <form onSubmit={handleConvert} className="flex flex-wrap items-end gap-3">
          <div>
            <label className="block text-xs font-medium text-gray-500">
              Amount
            </label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              required
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="mt-1 w-28 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-500">
              From
            </label>
            <select
              value={base}
              onChange={(e) => setBase(e.target.value)}
              className="mt-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {currencies.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <span className="pb-2 text-gray-400">&rarr;</span>
          <div>
            <label className="block text-xs font-medium text-gray-500">
              To
            </label>
            <select
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              className="mt-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              {currencies.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            disabled={convert.isPending}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {convert.isPending ? "..." : "Convert"}
          </button>
        </form>

        {convert.data && (
          <div className="mt-4 rounded-lg bg-indigo-50 px-4 py-3">
            <p className="text-lg font-semibold text-indigo-700">
              {parseFloat(convert.data.original_amount).toFixed(2)}{" "}
              {convert.data.base} ={" "}
              {parseFloat(convert.data.converted_amount).toFixed(2)}{" "}
              {convert.data.target}
            </p>
            <p className="text-xs text-indigo-500">
              Rate: 1 {convert.data.base} = {convert.data.rate.toFixed(4)}{" "}
              {convert.data.target}
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
