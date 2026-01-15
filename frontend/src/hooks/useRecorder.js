import { useRef, useState } from "react";

export default function useRecorder() {
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);

  const [recording, setRecording] = useState(false);

  async function startRecording(videoEl) {
    streamRef.current = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });

    videoEl.srcObject = streamRef.current;

    mediaRecorderRef.current = new MediaRecorder(streamRef.current);
    chunksRef.current = [];

    mediaRecorderRef.current.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    mediaRecorderRef.current.start();
    setRecording(true);
  }

  function stopRecording() {
    return new Promise((resolve) => {
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "video/webm" });
        streamRef.current.getTracks().forEach((t) => t.stop());
        setRecording(false);
        resolve(blob);
      };
      mediaRecorderRef.current.stop();
    });
  }

  return {
    recording,
    startRecording,
    stopRecording
  };
}
