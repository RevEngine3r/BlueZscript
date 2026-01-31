package com.revengine3r.bluezscript.domain.usecases

import com.revengine3r.bluezscript.data.models.BleMessage
import com.revengine3r.bluezscript.data.models.PairedDevice
import com.revengine3r.bluezscript.data.repository.DeviceRepository
import com.revengine3r.bluezscript.domain.ble.BleService
import com.revengine3r.bluezscript.domain.crypto.TotpManager
import javax.inject.Inject

/**
 * Use case for triggering an action on Raspberry Pi.
 */
class TriggerActionUseCase @Inject constructor(
    private val bleService: BleService,
    private val totpManager: TotpManager,
    private val deviceRepository: DeviceRepository
) {
    suspend operator fun invoke(device: PairedDevice): Result<Unit> {
        return try {
            // Generate TOTP
            val totp = totpManager.generateTotp(device.secretKey)
            
            // Create BLE message
            val message = BleMessage(
                deviceId = device.id,
                totp = totp,
                timestamp = System.currentTimeMillis() / 1000,
                action = "TRIGGER"
            )
            
            // Send via BLE
            bleService.sendMessage(message)
            
            // Update last used
            deviceRepository.updateLastUsed(device.id)
            
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
