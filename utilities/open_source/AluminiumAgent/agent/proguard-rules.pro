# Entry points invoked by app_process.
-keep class com.microsoft.hobl.agent.Server {
    public static void main(java.lang.String[]);
}
-keep class com.microsoft.hobl.agent.ScreenServer {
    public static void main(java.lang.String[]);
}
-keep class com.microsoft.hobl.agent.WallpaperTool {
    public static void main(java.lang.String[]);
}
