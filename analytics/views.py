# from django.http import HttpResponse, JsonResponse
# from django.shortcuts import render
# from django.core.files.storage import FileSystemStorage
# import pandas as pd
# import io

# def index(request):
#     """Render the homepage."""
#     return render(request, 'analytics/index.html')

# def procedures(request):
#     """Render the procedures page."""
#     return render(request, 'analytics/procedures.html')

# # def wrangle(path):
# #     """Process the uploaded file."""
# #     df = pd.read_excel(path)
# #     df.columns = ["Device", "Status", "Start", "End", "Duration", "Stop position", "Fuel consumption"]
# #     df.dropna(subset=["Device", "Status", "Start", "End", "Duration", "Stop position", "Fuel consumption"], inplace=True)
# #     df.drop(columns=["Fuel consumption"], inplace=True)
# #     mask_stopped = df["Status"] == "Stopped"
# #     df = df[mask_stopped]
# #     lat_long = df["Stop position"].str.split(",", expand=True)
# #     lat_long.columns = ["Latitude", "Longitude"]
# #     df[["Latitude", "Longitude"]] = lat_long.astype(float).round(4)
# #     df["Concat_location_rounded"] = df["Latitude"].astype(str) + "," + df["Longitude"].astype(str)
# #     df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
# #     df["End"] = pd.to_datetime(df["End"], errors="coerce")
# #     df["Duration_Calcuated_minutes"] = ((df["End"] - df["Start"]).dt.total_seconds() / 60).round(2)
# #     df[df["Duration_Calcuated_minutes"] > 30]
# #     df = pd.pivot_table(df, index=["Concat_location_rounded"], aggfunc="size").reset_index(name='Stop_Count').sort_values(by="Stop_Count", ascending=False)
# #     return df

# def process_file(request):
#     """Handle file upload and processing."""
#     if request.method == 'POST' and request.FILES.get('file'):
#         file = request.FILES['file']
#         fs = FileSystemStorage()
#         filename = fs.save(file.name, file)
#         file_path = fs.path(filename)

#         try:
#             # Process file
#             df = wrangle(file_path)
#             pivot_data_gps = pd.pivot_table(df, index=["Concat_location_rounded"], aggfunc="size").reset_index(name='Stop_Count').sort_values(by="Stop_Count", ascending=False)

#             # Save processed data
#             output = io.BytesIO()
#             with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#                 df.to_excel(writer, index=False, sheet_name='Cleaned Data')
#                 pivot_data_gps.to_excel(writer, index=False, sheet_name='Pivot Table')

#             output.seek(0)
#             response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#             response['Content-Disposition'] = 'attachment; filename=processed_file.xlsx'
#             return response

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request'}, status=400)


from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import pandas as pd
import io

def index(request):
    """Render the homepage."""
    return render(request, 'analytics/index.html')

def procedures(request):
    """Render the procedures page."""
    return render(request, 'analytics/procedures.html')

def wrangle(path):
    """
    Cleans and filters Excel data for two duration ranges:
    - 30–300 minutes
    - >300 minutes
    Returns:
        df1, pivot1, df2, pivot2
    """
    df = pd.read_excel(path)
    df.columns = ["Device", "Status", "Start", "End", "Duration", "Stop position", "Fuel consumption"]
    df.dropna(subset=["Device", "Status", "Start", "End", "Duration", "Stop position", "Fuel consumption"], inplace=True)
    df.drop(df.index[0], inplace=True)
    df.drop(columns=["Fuel consumption"], inplace=True)
    df = df[df["Status"] == "Stopped"]

    lat_long = df["Stop position"].str.split(",", expand=True)
    lat_long.columns = ["Latitude", "Longitude"]
    df[["Latitude", "Longitude"]] = lat_long.astype(float).round(4)
    df["Concat_location_rounded"] = df["Latitude"].astype(str) + "," + df["Longitude"].astype(str)

    df["Start"] = pd.to_datetime(df["Start"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df["End"] = pd.to_datetime(df["End"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df["Duration_Calcuated_minutes"] = ((df["End"] - df["Start"]).dt.total_seconds() / 60).round(2)

    # 30–300 minutes
    df1 = df[(df["Duration_Calcuated_minutes"] > 30) & (df["Duration_Calcuated_minutes"] < 300)].copy()
    pivot1 = df1.groupby("Concat_location_rounded").size().reset_index(name="Stop_Count").sort_values(by="Stop_Count", ascending=False)

    # >300 minutes
    df2 = df[df["Duration_Calcuated_minutes"] > 300].copy()
    pivot2 = df2.groupby("Concat_location_rounded").size().reset_index(name="Stop_Count").sort_values(by="Stop_Count", ascending=False)

    return df1, pivot1, df2, pivot2

def process_file(request):
    """Handle file upload and return multi-sheet Excel download."""
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = fs.path(filename)

        try:
            # Process file using combined wrangle function
            df1, pivot1, df2, pivot2 = wrangle(file_path)

            # Prepare Excel output with multiple sheets
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df1.to_excel(writer, index=False, sheet_name='30-300 Minutes')
                pivot1.to_excel(writer, index=False, sheet_name='Pivot 30-300')
                df2.to_excel(writer, index=False, sheet_name='Above 300 Minutes')
                pivot2.to_excel(writer, index=False, sheet_name='Pivot >300')

            output.seek(0)
            response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=processed_stops_analysis.xlsx'
            return response

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)
