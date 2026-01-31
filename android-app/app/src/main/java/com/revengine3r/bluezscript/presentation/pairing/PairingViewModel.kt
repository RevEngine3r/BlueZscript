package com.revengine3r.bluezscript.presentation.pairing

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.revengine3r.bluezscript.data.models.PairingData
import com.revengine3r.bluezscript.domain.usecases.PairDeviceUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import javax.inject.Inject

/**
 * ViewModel for Pairing screen.
 */
@HiltViewModel
class PairingViewModel @Inject constructor(
    private val pairDeviceUseCase: PairDeviceUseCase
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(PairingUiState())
    val uiState: StateFlow<PairingUiState> = _uiState.asStateFlow()
    
    private val json = Json { ignoreUnknownKeys = true }
    
    fun onQrCodeScanned(qrData: String) {
        try {
            val pairingData = json.decodeFromString<PairingData>(qrData)
            _uiState.update { it.copy(
                pairingData = pairingData,
                showNameDialog = true,
                error = null
            ) }
        } catch (e: Exception) {
            _uiState.update { it.copy(
                error = "Invalid QR code format"
            ) }
        }
    }
    
    fun onDeviceNameEntered(name: String) {
        _uiState.update { it.copy(deviceName = name) }
    }
    
    fun completePairing() {
        val pairingData = _uiState.value.pairingData ?: return
        val deviceName = _uiState.value.deviceName.trim()
        
        if (deviceName.isEmpty()) {
            _uiState.update { it.copy(error = "Device name cannot be empty") }
            return
        }
        
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            
            pairDeviceUseCase(pairingData, deviceName)
                .onSuccess {
                    _uiState.update { it.copy(
                        isLoading = false,
                        isPairingComplete = true
                    ) }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(
                        isLoading = false,
                        error = error.message ?: "Failed to pair device"
                    ) }
                }
        }
    }
    
    fun dismissDialog() {
        _uiState.update { it.copy(showNameDialog = false) }
    }
    
    fun clearError() {
        _uiState.update { it.copy(error = null) }
    }
}

data class PairingUiState(
    val pairingData: PairingData? = null,
    val deviceName: String = "",
    val showNameDialog: Boolean = false,
    val isLoading: Boolean = false,
    val isPairingComplete: Boolean = false,
    val error: String? = null
)
