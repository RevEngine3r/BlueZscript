package com.revengine3r.bluezscript.presentation.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.revengine3r.bluezscript.presentation.home.HomeScreen
import com.revengine3r.bluezscript.presentation.pairing.PairingScreen
import com.revengine3r.bluezscript.presentation.settings.SettingsScreen

/**
 * Main navigation graph for the app.
 */
@Composable
fun BlueZscriptNavigation(
    modifier: Modifier = Modifier,
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Home.route,
        modifier = modifier
    ) {
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToPairing = {
                    navController.navigate(Screen.Pairing.route)
                },
                onNavigateToSettings = {
                    navController.navigate(Screen.Settings.route)
                },
                onNavigateToDevice = { deviceId ->
                    navController.navigate(Screen.DeviceDetail.createRoute(deviceId))
                }
            )
        }
        
        composable(Screen.Pairing.route) {
            PairingScreen(
                onNavigateBack = {
                    navController.popBackStack()
                },
                onPairingComplete = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(Screen.Settings.route) {
            SettingsScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
    }
}
