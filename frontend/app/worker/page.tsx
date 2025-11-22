"use client";

import { useState, useRef, useCallback } from "react";
import { Camera, MapPin, Upload, Loader2, CheckCircle2, XCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";
import Webcam from "react-webcam";
import { api } from "@/utils/api";

type Step = "details" | "photo" | "gesture" | "processing" | "result";

export default function WorkerPortal() {
  const [step, setStep] = useState<Step>("details");
  const [workerId, setWorkerId] = useState("WORKER001");
  const [trees, setTrees] = useState(25);
  const [location, setLocation] = useState("");
  const [gpsCoords, setGpsCoords] = useState("");
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [plantId, setPlantId] = useState(""); // Joyo plant ID (optional)
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlobUrl, setRecordedBlobUrl] = useState<string | null>(null);
  const [recordedFile, setRecordedFile] = useState<File | null>(null);
  const [gestureCount, setGestureCount] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const webcamRef = useRef<Webcam>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<BlobPart[]>([]);

  // Auto-detect GPS location
  const detectLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setGpsCoords(`${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
          // In production, reverse geocode to get location name
          setLocation("Mumbai, Maharashtra, India");
        },
        (error) => {
          console.error("Geolocation error:", error);
          setError("Could not detect location. Please enter manually.");
        }
      );
    }
  };

  // Handle photo upload
  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setPhotoFile(file);
      setPhotoPreview(URL.createObjectURL(file));
    }
  };

  // Capture photo from webcam
  const capturePhoto = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setPhotoPreview(imageSrc);
      // Convert base64 to file
      fetch(imageSrc)
        .then((res) => res.blob())
        .then((blob) => {
          const file = new File([blob], "tree-photo.jpg", { type: "image/jpeg" });
          setPhotoFile(file);
        });
    }
  }, [webcamRef]);

  // Start video recording
  const startRecording = async () => {
    try {
      setError(null);
      let stream: MediaStream | undefined;
      const webcamAny: any = webcamRef.current as any;
      const videoEl: HTMLVideoElement | undefined = webcamAny?.video;
      if (videoEl && (videoEl as any).srcObject) {
        stream = (videoEl as any).srcObject as MediaStream;
      } else {
        stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      }

      const supported = [
        'video/webm;codecs=vp9',
        'video/webm;codecs=vp8',
        'video/webm',
      ];
      const mimeType = supported.find((t) => (window as any).MediaRecorder?.isTypeSupported?.(t)) || '';
      const options = mimeType ? { mimeType } : undefined as any;

      recordedChunksRef.current = [];
      mediaRecorderRef.current = new MediaRecorder(stream!, options);
      mediaRecorderRef.current.ondataavailable = (e: BlobEvent) => {
        if (e.data && e.data.size > 0) recordedChunksRef.current.push(e.data);
      };
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(recordedChunksRef.current, { type: mimeType || 'video/webm' });
        const file = new File([blob], 'watering.webm', { type: blob.type });
        setRecordedFile(file);
        const url = URL.createObjectURL(blob);
        setRecordedBlobUrl(url);
      };
      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (e: any) {
      console.error(e);
      setError('Unable to access camera for recording');
    }
  };

  const stopRecording = () => {
    try {
      mediaRecorderRef.current?.stop();
    } finally {
      setIsRecording(false);
    }
  };

  const uploadWateringToJoyo = async () => {
    try {
      setError(null);
      if (!plantId) {
        setError('Please enter your Joyo Plant ID');
        return;
      }
      if (!recordedFile) {
        setError('No watering video recorded');
        return;
      }
      const [latStr, lngStr] = (gpsCoords || '').split(',').map((s) => s.trim());
      const lat = parseFloat(latStr);
      const lng = parseFloat(lngStr);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
        setError('Invalid GPS coordinates');
        return;
      }
      setIsProcessing(true);
      const resp = await api.joyoRecordWatering(plantId, recordedFile, lat, lng);
      setResult(resp);
      setStep('result');
    } catch (e: any) {
      console.error(e);
      setError(e?.message || 'Failed to upload watering video');
    } finally {
      setIsProcessing(false);
    }
  };

  // Simulate gesture detection (in production, use MediaPipe)
  const startGestureDetection = () => {
    let count = 0;
    const interval = setInterval(() => {
      count++;
      setGestureCount(count);
      if (count >= 5) {
        clearInterval(interval);
        setTimeout(() => setStep("processing"), 500);
      }
    }, 2000);
  };

  // Submit verification
  const submitVerification = async () => {
    setIsProcessing(true);
    setError(null);

    try {
      // 1. Upload photo
      if (!photoFile) {
        throw new Error("No photo captured");
      }

      const uploadResult = await api.uploadImage(photoFile, workerId);
      console.log("Photo uploaded:", uploadResult);

      // 2. Submit verification
      const verificationData = {
        trees_planted: trees,
        location,
        gps_coords: gpsCoords,
        worker_id: workerId,
        image_url: uploadResult.url,
        verification_duration: 10,
      };

      const verificationResult = await api.submitVerification(verificationData);
      console.log("Verification result:", verificationResult);

      setResult(verificationResult);
      setStep("result");
    } catch (err: any) {
      console.error("Verification error:", err);
      setError(err.message || "Verification failed");
      setStep("result");
    } finally {
      setIsProcessing(false);
    }
  };

  // Reset form
  const resetForm = () => {
    setStep("details");
    setTrees(25);
    setLocation("");
    setGpsCoords("");
    setPhotoFile(null);
    setPhotoPreview(null);
    setGestureCount(0);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-2 text-green-600">
            <ArrowLeft className="h-5 w-5" />
            <span className="font-semibold">Back to Home</span>
          </Link>
          <div className="text-sm text-gray-600">Worker ID: {workerId}</div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 max-w-2xl">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            {["Details", "Photo", "Gesture", "Verify"].map((label, i) => (
              <div
                key={label}
                className={`text-sm font-medium ${
                  i <= ["details", "photo", "gesture", "processing", "result"].indexOf(step)
                    ? "text-green-600"
                    : "text-gray-400"
                }`}
              >
                {label}
              </div>
            ))}
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-600 transition-all duration-500"
              style={{
                width: `${
                  (["details", "photo", "gesture", "processing", "result"].indexOf(step) / 4) * 100
                }%`,
              }}
            />
          </div>
        </div>

        {/* Step 1: Details */}
        {step === "details" && (
          <div className="bg-white rounded-xl shadow-md p-8">
            <h2 className="text-2xl font-bold mb-6">New Verification</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Worker ID</label>
                <input
                  type="text"
                  value={workerId}
                  onChange={(e) => setWorkerId(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                  placeholder="WORKER001"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Trees Planted</label>
                <input
                  type="number"
                  value={trees}
                  onChange={(e) => setTrees(parseInt(e.target.value))}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                  min="1"
                  max="1000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Location</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                    placeholder="Mumbai, Maharashtra, India"
                  />
                  <button
                    onClick={detectLocation}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                  >
                    <MapPin className="h-5 w-5" />
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">GPS Coordinates</label>
                <input
                  type="text"
                  value={gpsCoords}
                  onChange={(e) => setGpsCoords(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                  placeholder="19.076000, 72.877000"
                />
                <p className="text-xs text-gray-500 mt-1">Auto-detected or enter manually</p>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Joyo Plant ID (optional for watering upload)</label>
                <input
                  type="text"
                  value={plantId}
                  onChange={(e) => setPlantId(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
                  placeholder="e.g., PLANT_ABC12345"
                />
              </div>

              <button
                onClick={() => setStep("photo")}
                disabled={!trees || !location || !gpsCoords}
                className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
              >
                Next: Capture Photo
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Photo */}
        {step === "photo" && (
          <div className="bg-white rounded-xl shadow-md p-8">
            <h2 className="text-2xl font-bold mb-6">Capture Tree Photo</h2>

            <div className="space-y-4">
              {!photoPreview ? (
                <div>
                  <div className="bg-gray-100 rounded-lg p-8 mb-4">
                    <Webcam
                      ref={webcamRef}
                      audio={false}
                      screenshotFormat="image/jpeg"
                      className="w-full rounded-lg"
                    />
                  </div>
                  <button
                    onClick={capturePhoto}
                    className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition flex items-center justify-center gap-2"
                  >
                    <Camera className="h-5 w-5" />
                    Capture Photo
                  </button>
                  <div className="text-center my-4 text-gray-500">or</div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handlePhotoChange}
                    className="hidden"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition flex items-center justify-center gap-2"
                  >
                    <Upload className="h-5 w-5" />
                    Upload Photo
                  </button>
                </div>
              ) : (
                <div>
                  <img
                    src={photoPreview}
                    alt="Tree photo"
                    className="w-full rounded-lg mb-4"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setPhotoPreview(null);
                        setPhotoFile(null);
                      }}
                      className="flex-1 py-3 bg-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-400 transition"
                    >
                      Retake
                    </button>
                    <button
                      onClick={() => setStep("gesture")}
                      className="flex-1 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition"
                    >
                      Next: Gestures
                    </button>
                  </div>

                  {/* Optional: Watering Video Recording for Joyo */}
                  <div className="mt-8 border-t pt-6">
                    <h3 className="text-xl font-semibold mb-4">Watering Video (Optional - Joyo)</h3>
                    {!recordedBlobUrl && (
                      <div className="flex gap-2">
                        {!isRecording ? (
                          <button
                            onClick={startRecording}
                            className="flex-1 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                          >
                            Start Recording
                          </button>
                        ) : (
                          <button
                            onClick={stopRecording}
                            className="flex-1 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition"
                          >
                            Stop Recording
                          </button>
                        )}
                      </div>
                    )}
                    {recordedBlobUrl && (
                      <div>
                        <video src={recordedBlobUrl} controls className="w-full rounded-lg mb-3" />
                        <div className="flex gap-2">
                          <button
                            onClick={() => { setRecordedBlobUrl(null); setRecordedFile(null); }}
                            className="flex-1 py-3 bg-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-400 transition"
                          >
                            Discard
                          </button>
                          <button
                            onClick={uploadWateringToJoyo}
                            disabled={!plantId}
                            className="flex-1 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
                          >
                            Upload to Joyo
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Gesture */}
        {step === "gesture" && (
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            <h2 className="text-2xl font-bold mb-6">Verify Your Identity</h2>
            <p className="text-gray-600 mb-8">
              Show hand gestures (👍 or 🤏) for 10 seconds
            </p>

            <div className="bg-gray-100 rounded-lg p-8 mb-6">
              <div className="text-6xl mb-4">✋</div>
              <div className="text-4xl font-bold text-green-600 mb-2">{gestureCount}/5</div>
              <div className="text-gray-600">Gestures Detected</div>
            </div>

            {gestureCount === 0 && (
              <button
                onClick={startGestureDetection}
                className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition"
              >
                Start Gesture Detection
              </button>
            )}

            {gestureCount > 0 && gestureCount < 5 && (
              <div className="text-green-600 font-semibold animate-pulse">
                Keep showing gestures...
              </div>
            )}
          </div>
        )}

        {/* Step 4: Processing */}
        {step === "processing" && (
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            <h2 className="text-2xl font-bold mb-6">Validating...</h2>

            <div className="space-y-4 mb-8">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
                <span>Gesture verified</span>
              </div>
              <div className="flex items-center gap-3">
                <CheckCircle2 className="h-6 w-6 text-green-600" />
                <span>GPS validated</span>
              </div>
              <div className="flex items-center gap-3">
                <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
                <span>AI analyzing...</span>
              </div>
              <div className="flex items-center gap-3">
                <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
                <span>Minting NFT...</span>
              </div>
            </div>

            {!isProcessing && (
              <button
                onClick={submitVerification}
                className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition"
              >
                Submit Verification
              </button>
            )}

            {isProcessing && (
              <div className="text-gray-600">Please wait, this takes ~30 seconds...</div>
            )}
          </div>
        )}

        {/* Step 5: Result */}
        {step === "result" && (
          <div className="bg-white rounded-xl shadow-md p-8 text-center">
            {result?.success ? (
              <>
                <CheckCircle2 className="h-20 w-20 text-green-600 mx-auto mb-4" />
                <h2 className="text-3xl font-bold text-green-600 mb-4">Success!</h2>
                <p className="text-gray-600 mb-6">Your carbon credit NFT has been minted</p>

                <div className="bg-green-50 rounded-lg p-6 mb-6 text-left">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600">Asset ID</div>
                      <div className="font-semibold">{result.asset_id}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Carbon Offset</div>
                      <div className="font-semibold">{result.carbon_offset_kg} kg CO₂</div>
                    </div>
                    <div className="col-span-2">
                      <div className="text-sm text-gray-600">Transaction ID</div>
                      <div className="font-mono text-xs break-all">{result.transaction_id}</div>
                    </div>
                  </div>
                </div>

                {result.explorer_url && (
                  <a
                    href={result.explorer_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition mb-3"
                  >
                    View on Explorer
                  </a>
                )}

                <button
                  onClick={resetForm}
                  className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition"
                >
                  New Verification
                </button>
              </>
            ) : (
              <>
                <XCircle className="h-20 w-20 text-red-600 mx-auto mb-4" />
                <h2 className="text-3xl font-bold text-red-600 mb-4">Verification Failed</h2>
                <p className="text-gray-600 mb-6">{error || result?.message}</p>

                <button
                  onClick={resetForm}
                  className="w-full py-3 bg-gray-600 text-white rounded-lg font-semibold hover:bg-gray-700 transition"
                >
                  Try Again
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
