package com.revengine3r.bluezscript.presentation.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.revengine3r.bluezscript.data.models.PairedDevice
import com.revengine3r.bluezscript.domain.usecases.GetDevicesUseCase
import com.revengine3r.bluezscript.domain.usecases.RemoveDeviceUseCase
import com.revengine3r.bluezscript.domain.usecases.TriggerActionUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * ViewModel for Home screen.
 */
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getDevicesUseCase: GetDevicesUseCase,
    private val triggerActionUseCase: TriggerActionUseCase,
    private val removeDeviceUseCase: RemoveDeviceUseCase
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()
    
    init {
        loadDevices()
    }
    
    private fun loadDevices() {
        viewModelScope.launch {
            getDevicesUseCase().collect { devices ->
                _uiState.update { it.copy(
                    devices = devices,
                    isLoading = false
                ) }
            }
        }
    }
    
    fun triggerAction(device: PairedDevice) {
        viewModelScope.launch {
            _uiState.update { it.copy(isTriggering = true, error = null) }
            
            triggerActionUseCase(device)
                .onSuccess {
                    _uiState.update { it.copy(
                        isTriggering = false,
                        successMessage = "Action triggered successfully!"
                    ) }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(
                        isTriggering = false,
                        error = error.message ?: "Failed to trigger action"
                    ) }
                }
        }
    }
    
    fun removeDevice(deviceId: String) {
        viewModelScope.launch {
            removeDeviceUseCase(deviceId)
                .onSuccess {
                    _uiState.update { it.copy(
                        successMessage = "Device removed"
                    ) }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(
                        error = error.message ?: "Failed to remove device"
                    ) }
                }
        }
    }
    
    fun clearMessages() {
        _uiState.update { it.copy(error = null, successMessage = null) }
    }
}

data class HomeUiState(
    val devices: List<PairedDevice> = emptyList(),
    val isLoading: Boolean = true,
    val isTriggering: Boolean = false,
    val error: String? = null,
    val successMessage: String? = null
)
