export type RaspberryPiConnectionStatus = {
  connected: boolean;
  mode: "demo" | "raspberry_pi";
  latencyMs: number | null;
  fps: number | null;
  modelName: string | null;
  lastSignalAt: string | null;
  message: string;
};
