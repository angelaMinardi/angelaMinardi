import { useEffect } from 'react';
import { useGaitStore } from '../store/gaitStore';
import { predictRisk } from '../api/client';

export function useGaitData() {
  const { liveSamples, latestFeatures, setCurrentRisk } = useGaitStore();

  useEffect(() => {
    if (liveSamples.length > 0 && liveSamples.length % 100 === 0 && latestFeatures) {
      predictRisk(latestFeatures).then(setCurrentRisk).catch(console.error);
    }
  }, [liveSamples.length, latestFeatures, setCurrentRisk]);

  return {
    sampleCount: liveSamples.length,
    latestSample: liveSamples[liveSamples.length - 1] ?? null,
  };
}
