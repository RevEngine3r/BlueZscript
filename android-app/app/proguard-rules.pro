# Add project specific ProGuard rules here.

# Keep TOTP library classes
-keep class dev.turingcomplete.kotlinonetimepassword.** { *; }

# Keep data models (for JSON serialization)
-keep class com.revengine3r.bluezscript.data.models.** { *; }

# Keep Room entities
-keep class com.revengine3r.bluezscript.data.local.entity.** { *; }

# Kotlinx Serialization
-keepattributes *Annotation*, InnerClasses
-dontnote kotlinx.serialization.AnnotationsKt

-keepclassmembers class kotlinx.serialization.json.** {
    *** Companion;
}
-keepclasseswithmembers class kotlinx.serialization.json.** {
    kotlinx.serialization.KSerializer serializer(...);
}

# Keep Hilt generated code
-keep class dagger.hilt.** { *; }
-keep class javax.inject.** { *; }
-keep class * extends dagger.hilt.android.internal.managers.ViewComponentManager$FragmentContextWrapper { *; }
