import { AxiosError } from "axios";
import { useToast } from "@/context/ToastContext";

interface ValidationError {
  msg?: string;
  [key: string]: unknown;
}

interface AxiosErrorResponse {
  error?: string;
  errors?: ValidationError[];
  [key: string]: unknown;
}

export function showApiError(toast: ReturnType<typeof useToast>, err: unknown) {
  if (!err) return;

  let message = "Unknown error";
  let code: number | undefined = undefined;

  if ((err as AxiosError).isAxiosError) {
    const axiosErr = err as AxiosError<AxiosErrorResponse>;
    code = axiosErr.response?.status;

    if (axiosErr.response?.data) {
      const data = axiosErr.response.data;

      // Handle array of validation errors
      if (Array.isArray(data.errors)) {
        message = data.errors
          .map((e) => {
            if (typeof e === "string") return e;
            if (e?.msg) return e.msg;
            return JSON.stringify(e);
          })
          .join("\n");
      } else if (typeof data.error === "string") {
        message = data.error;
      } else {
        message = JSON.stringify(data);
      }
    } else {
      message = axiosErr.message;
    }
  } else if (err instanceof Error) {
    message = err.message;
  }

  toast.addToast(message, "error", code);
}
