import { useMutation } from "@tanstack/react-query";
import api from "../lib/api";
import type {
  CurrencyConvertApiResponse,
  CurrencyConvertResponse,
} from "../lib/types";

const parseApiNumber = (value: string | number, fieldName: string): number => {
  const parsedValue =
    typeof value === "number" ? value : Number.parseFloat(value);
  if (Number.isNaN(parsedValue)) {
    throw new Error(`Invalid currency conversion field: ${fieldName}`);
  }
  return parsedValue;
};

export function useCurrencyConvert() {
  return useMutation({
    mutationFn: (data: { amount: string; base: string; target: string }) =>
      api
        .post<CurrencyConvertApiResponse>("/currency/convert", data)
        .then((r): CurrencyConvertResponse => ({
          base: r.data.base,
          target: r.data.target,
          rate: parseApiNumber(r.data.rate, "rate"),
          original_amount: parseApiNumber(r.data.original_amount, "original_amount"),
          converted_amount: parseApiNumber(
            r.data.converted_amount,
            "converted_amount",
          ),
        })),
  });
}
