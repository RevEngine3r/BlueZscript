package com.revengine3r.bluezscript.presentation.navigation

/**
 * Sealed class representing all app screens.
 */
sealed class Screen(val route: String) {
    object Home : Screen("home")
    object Pairing : Screen("pairing")
    object DeviceDetail : Screen("device/{deviceId}") {
        fun createRoute(deviceId: String) = "device/$deviceId"
    }
    object Settings : Screen("settings")
}
