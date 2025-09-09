import { AxiosError } from "axios";
import { useToast } from "@/context/ToastContext";

export function showApiError(toast: ReturnType<typeof useToast>, err: any) {
  if (!err) return;

  let message = "Unknown error";
  let code: number | undefined = undefined;

  if ((err as AxiosError).isAxiosError) {
    const axiosErr = err as AxiosError;
    code = axiosErr.response?.status;

    if (axiosErr.response?.data) {
      const data = axiosErr.response.data as any;

      // Handle array of validation errors from e.errors()
      if (Array.isArray(data.errors)) {
        message = data.errors.map((e: any) => {
          if (typeof e === "string") return e;
          if (e?.msg) return e.msg;
          return JSON.stringify(e);
        }).join("\n");
      } else if (typeof data.error === "string") {
        // Single error message
        message = data.error;
      } else {
        message = JSON.stringify(data);
      }
    } else {
      message = axiosErr.message;
    }
  } else if (err.message) {
    message = err.message;
  }

  toast.addToast(message, "error", code);
}
