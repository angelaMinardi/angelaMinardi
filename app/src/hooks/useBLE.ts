import { useCallback, useRef, useState } from 'react';
import { useGaitStore } from '../store/gaitStore';
import type { GaitSample } from '../types';

const SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0';
const GAIT_DATA_UUID = '12345678-1234-5678-1234-56789abcdef1';

function parseGaitPacket(buffer: ArrayBuffer): GaitSample {
  const view = new DataView(buffer);
  const fsr: number[] = [];
  for (let i = 0; i < 8; i++) {
    fsr.push(view.getUint16(6 + i * 2, true));
  }
  return {
    timestamp: view.getUint32(2, true),
    fsr,
    accel: [
      view.getInt16(22, true),
      view.getInt16(24, true),
      view.getInt16(26, true),
    ],
    gyro: [
      view.getInt16(28, true),
      view.getInt16(30, true),
      view.getInt16(32, true),
    ],
    stepCount: view.getUint16(34, true),
    battery: view.getUint8(36),
  };
}

export function useBLE() {
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const charRef = useRef<BluetoothRemoteGATTCharacteristic | null>(null);
  const { setConnected, addSample } = useGaitStore();

  const connect = useCallback(async () => {
    if (!navigator.bluetooth) {
      setError('Web Bluetooth API not available. Use Chrome or Edge.');
      return;
    }
    setScanning(true);
    setError(null);
    try {
      const device = await navigator.bluetooth.requestDevice({
        filters: [{ namePrefix: 'SmartInsole' }],
        optionalServices: [SERVICE_UUID],
      });

      device.addEventListener('gattserverdisconnected', () => {
        setConnected(false);
        charRef.current = null;
      });

      const server = await device.gatt!.connect();
      const service = await server.getPrimaryService(SERVICE_UUID);
      const characteristic = await service.getCharacteristic(GAIT_DATA_UUID);
      charRef.current = characteristic;

      await characteristic.startNotifications();
      characteristic.addEventListener(
        'characteristicvaluechanged',
        (event: Event) => {
          const target = event.target as BluetoothRemoteGATTCharacteristic;
          if (target.value) {
            const sample = parseGaitPacket(target.value.buffer);
            addSample(sample);
          }
        }
      );

      setConnected(true, device.name ?? 'SmartInsole');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Connection failed');
    } finally {
      setScanning(false);
    }
  }, [setConnected, addSample]);

  const disconnect = useCallback(() => {
    if (charRef.current?.service?.device?.gatt?.connected) {
      charRef.current.service.device.gatt.disconnect();
    }
    setConnected(false);
    charRef.current = null;
  }, [setConnected]);

  return { connect, disconnect, scanning, error };
}
