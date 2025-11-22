// API client for Carbon Credit backend

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const JOYO_API_URL = process.env.NEXT_PUBLIC_JOYO_API_URL || 'http://localhost:8001';

export interface VerificationRequest {
  trees_planted: number;
  location: string;
  gps_coords: string;
  worker_id: string;
  image_url: string;
  verification_duration?: number;
}

export interface VerificationResponse {
  success: boolean;
  transaction_id?: string;
  asset_id?: number;
  explorer_url?: string;
  gesture_signature?: string;
  carbon_offset_kg?: number;
  message: string;
}

export interface WorkerHistory {
  worker_id: string;
  total_trees_planted: number;
  total_carbon_offset_kg: number;
  verifications: any[];
}

async function fetchWithRetry(
  input: RequestInfo | URL,
  init?: RequestInit,
  retries: number = 2,
  backoffMs: number = 500
) {
  let attempt = 0;
  let lastError: any = null;
  while (attempt <= retries) {
    try {
      const res = await fetch(input, init);
      // Retry on transient status codes
      if (res.status === 429 || res.status === 408 || (res.status >= 500 && res.status <= 599)) {
        throw new Error(`Transient HTTP status ${res.status}`);
      }
      return res;
    } catch (err: any) {
      lastError = err;
      const msg = String(err?.message || '');
      // Retry on known transport issues (HTTP/2 GOAWAY, connection resets, incomplete envelopes)
      const isTransient =
        msg.includes('GOAWAY') ||
        msg.includes('server_shutting_down') ||
        msg.includes('incomplete envelope') ||
        msg.includes('ECONNRESET') ||
        msg.includes('ETIMEDOUT') ||
        msg.includes('NetworkError') ||
        msg.includes('Failed to fetch');

      if (attempt < retries && isTransient) {
        const delay = backoffMs * Math.pow(2, attempt);
        await new Promise((r) => setTimeout(r, delay));
        attempt += 1;
        continue;
      }
      break;
    }
  }
  throw lastError;
}

class CarbonCreditAPI {
  private baseURL: string;
  private joyoURL: string;

  constructor(baseURL: string = API_URL, joyoURL: string = JOYO_API_URL) {
    this.baseURL = baseURL;
    this.joyoURL = joyoURL;
  }

  // Health check
  async healthCheck() {
    const response = await fetchWithRetry(`${this.baseURL}/`);
    return response.json();
  }

  // Upload verification image
  async uploadImage(file: File, workerId: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('worker_id', workerId);

    const response = await fetchWithRetry(`${this.baseURL}/upload-verification-image`, {
      method: 'POST',
      body: formData,
    });

    return response.json();
  }

  // Submit verification
  async submitVerification(data: VerificationRequest): Promise<VerificationResponse> {
    const response = await fetchWithRetry(`${this.baseURL}/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    return response.json();
  }

  // Get worker history
  async getWorkerHistory(workerId: string, limit: number = 10): Promise<WorkerHistory> {
    const response = await fetchWithRetry(`${this.baseURL}/worker/${workerId}/history?limit=${limit}`);
    return response.json();
  }

  // Validate claim (pre-check)
  async validateClaim(trees: number, location: string, gps: string) {
    const response = await fetchWithRetry(`${this.baseURL}/validate-claim`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        trees_planted: trees,
        location,
        gps_coords: gps,
      }),
    });

    return response.json();
  }

  // Get system stats
  async getStats() {
    const response = await fetchWithRetry(`${this.baseURL}/stats`);
    return response.json();
  }

  // Check Algorand status
  async getAlgorandStatus() {
    const response = await fetchWithRetry(`${this.baseURL}/algorand/status`);
    return response.json();
  }

  // Admin: Get pending reviews
  async getPendingReviews() {
    const response = await fetchWithRetry(`${this.baseURL}/admin/pending-reviews`);
    return response.json();
  }

  // Admin: Approve verification
  async approveVerification(verificationId: string) {
    const response = await fetchWithRetry(`${this.baseURL}/admin/approve/${verificationId}`, {
      method: 'POST',
    });
    return response.json();
  }

  async joyoRecordWatering(plantId: string, videoFile: File, gpsLat: number, gpsLong: number) {
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('gps_latitude', String(gpsLat));
    formData.append('gps_longitude', String(gpsLong));

    const response = await fetchWithRetry(`${this.joyoURL}/plants/${encodeURIComponent(plantId)}/water`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  }
}

export const api = new CarbonCreditAPI();

