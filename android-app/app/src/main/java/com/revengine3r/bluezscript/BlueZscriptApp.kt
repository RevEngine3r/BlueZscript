package com.revengine3r.bluezscript

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Application class for BlueZscript.
 * Entry point for Hilt dependency injection.
 */
@HiltAndroidApp
class BlueZscriptApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // Initialize app-wide components here if needed
    }
}
