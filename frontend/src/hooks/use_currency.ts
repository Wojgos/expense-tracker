import { useMutation } from "@tanstack/react-query";
import api from "../lib/api";
import type { CurrencyConvertResponse } from "../lib/types";

export function useCurrencyConvert() {
  return useMutation({
    mutationFn: (data: { amount: string; base: string; target: string }) =>
      api
        .post<CurrencyConvertResponse>("/currency/convert", data)
        .then((r) => r.data),
  });
}
