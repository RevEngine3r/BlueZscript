package com.revengine3r.bluezscript

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.ui.Modifier
import com.revengine3r.bluezscript.presentation.navigation.BlueZscriptNavigation
import com.revengine3r.bluezscript.presentation.theme.BlueZscriptTheme
import dagger.hilt.android.AndroidEntryPoint

/**
 * Main activity hosting the Compose navigation graph.
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        
        setContent {
            BlueZscriptTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    BlueZscriptNavigation(
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}
