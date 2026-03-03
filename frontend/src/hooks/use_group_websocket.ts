import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";

export function useGroupWebSocket(groupId: string, token: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const qc = useQueryClient();

  useEffect(() => {
    if (!token) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const url = `${protocol}//${host}/ws/groups/${groupId}?token=${token}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case "expense_created":
          toast(`New expense: ${data.description} (${data.amount})`, {
            icon: "💸",
          });
          qc.invalidateQueries({ queryKey: ["expenses", groupId] });
          qc.invalidateQueries({ queryKey: ["settlements", groupId] });
          break;

        case "settlement_created":
          toast(
            `${data.payer_name} paid ${data.receiver_name} ${data.amount}`,
            { icon: "✅" },
          );
          qc.invalidateQueries({ queryKey: ["settlements", groupId] });
          break;

        case "recurring_expense_generated":
          toast(`Recurring expense: ${data.description}`, { icon: "🔄" });
          qc.invalidateQueries({ queryKey: ["expenses", groupId] });
          qc.invalidateQueries({ queryKey: ["settlements", groupId] });
          break;
      }
    };

    ws.onclose = () => {
      wsRef.current = null;
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [groupId, token, qc]);
}
