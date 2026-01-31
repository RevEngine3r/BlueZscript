package com.revengine3r.bluezscript.domain.crypto

import dev.turingcomplete.kotlinonetimepassword.HmacAlgorithm
import dev.turingcomplete.kotlinonetimepassword.TimeBasedOneTimePasswordConfig
import dev.turingcomplete.kotlinonetimepassword.TimeBasedOneTimePasswordGenerator
import org.apache.commons.codec.binary.Base32
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Manager for TOTP generation.
 */
@Singleton
class TotpManager @Inject constructor() {
    
    private val config = TimeBasedOneTimePasswordConfig(
        codeDigits = 6,
        hmacAlgorithm = HmacAlgorithm.SHA1,
        timeStep = 30,
        timeStepUnit = TimeUnit.SECONDS
    )
    
    /**
     * Generate TOTP code from secret.
     * 
     * @param secret Base32-encoded secret
     * @return 6-digit TOTP code
     */
    fun generateTotp(secret: String): String {
        val secretBytes = Base32().decode(secret)
        val generator = TimeBasedOneTimePasswordGenerator(secretBytes, config)
        return generator.generate()
    }
    
    /**
     * Validate TOTP code.
     * 
     * @param secret Base32-encoded secret
     * @param code TOTP code to validate
     * @return true if valid
     */
    fun validateTotp(secret: String, code: String): Boolean {
        val currentCode = generateTotp(secret)
        return currentCode == code
    }
}
